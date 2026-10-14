# ruff: noqa: N999 -- Preserve the public rrparser.Parser import path.
"""
Created on May 4 2020

@author: Joan Hérisson

"""

from __future__ import annotations

from collections.abc import Sequence
from csv import QUOTE_ALL, QUOTE_NONE
from logging import Logger, getLogger
from re import split
from tarfile import open as open_tar

from pandas import DataFrame, concat, read_csv

from .Args import (
    DEFAULT_RADII,
    DEFAULT_RELEASE,
    DEFAULT_RULES_DIR,
    DEFAULT_RULES_FILE,
)
from .Downloads import RR02_FILE, fetch_dataset, fetch_datasets

LOGGER = getLogger(__name__)


def read_ecnumbers(ec_file: str, logger: Logger = LOGGER) -> list[str]:
    """
    Read EC numbers from a file.

    Parameters
    ----------
    ec_file: str
        File containing EC numbers
    logger : Logger
        The logger object.

    Returns
    -------
    ecx: List[str]
        List of EC numbers.
    """
    logger.debug("Reading EC numbers from file...")
    with open(ec_file, "r") as f:
        ec = f.read().split(",")
        return ec


def _read_rules(rules_file, **read_options):
    if str(rules_file).endswith(".tar.gz"):
        with open_tar(rules_file, mode="r:gz") as archive:
            member = next(
                (
                    item
                    for item in archive
                    if item.name in (RR02_FILE, "./" + RR02_FILE) and item.isfile()
                ),
                None,
            )
            if member is None:
                raise ValueError(
                    f"RetroRules rr02 archive does not contain {RR02_FILE}"
                )
            with archive.extractfile(member) as source:
                return read_csv(source, **read_options)
    else:
        return read_csv(rules_file, **read_options)


def _merge_templates(frames):
    """Union shared template annotations and retain the best source score."""
    templates = concat(frames, ignore_index=True)
    duplicate = templates.duplicated("TEMPLATE_ID", keep=False)
    if not duplicate.any():
        return templates
    groups = templates[duplicate].groupby("TEMPLATE_ID", sort=False)
    if (groups["TEMPLATE"].nunique() > 1).any():
        raise ValueError("Conflicting SMARTS for the same template ID across datasets")

    def union(values):
        return ";".join(
            sorted(
                {
                    item
                    for value in values.dropna().astype(str)
                    for item in split(r"[;,]", value)
                    if item
                }
            )
        )

    aggregations = {
        column: "first" for column in templates.columns if column != "TEMPLATE_ID"
    }
    for column in ("REACTIONS", "ECS", "DATASETS", "RADII"):
        if column in aggregations:
            aggregations[column] = union
    aggregations["SCORE"] = "max"
    if "VALID" in aggregations:
        aggregations["VALID"] = "all"
    merged = groups.agg(aggregations).reset_index()
    for column in ("REACTIONS", "ECS"):
        if column + "_COUNT" in merged.columns:
            merged[column + "_COUNT"] = merged[column].map(
                lambda value: len(value.split(";")) if value else 0
            )
    if "RADII" in merged.columns:
        radii = merged["RADII"].map(
            lambda value: sorted(map(int, value.split(";"))) if value else []
        )
        merged["RADII"] = radii.map(lambda values: ";".join(map(str, values)))
        for column, position in (("RADIUS_MIN", 0), ("RADIUS_MAX", -1)):
            if column in merged.columns:
                merged[column] = radii.map(
                    lambda values, position=position: (
                        values[position] if values else None
                    )
                )
    result = concat([templates[~duplicate], merged], ignore_index=True)
    return (
        result.set_index("TEMPLATE_ID")
        .loc[templates["TEMPLATE_ID"].drop_duplicates()]
        .reset_index()
    )


def parse_rules(
    outfile: str | None,
    rules_file: str = DEFAULT_RULES_FILE,
    scores_file: str | None = None,
    rules_dir: str = DEFAULT_RULES_DIR,
    input_format: str = "csv",
    rule_type: str = "all",
    radii: Sequence[int] = DEFAULT_RADII,
    ecx: list[str] | None = None,
    ec: list[str] | None = None,
    output_format: str = "csv",
    logger: Logger = LOGGER,
    release: str = DEFAULT_RELEASE,
    dataset: str = "metanetx",
) -> str | None:
    """
    Parse reaction rules using normalized radii and rule usage filters.

    Parameters
    ----------
    rules_file: str
        Reactions file (if not set RetroRules are considered)
    scores_file: str
        Reactions scores file (if not set RetroRules are considered)
    rules_dir: str
        Source archive cache (default: cache directory inside the rrparser package).
    outfile: str
        Filename where to write results (if not set results are returned as a string)
    input_format: str
        Input format of rules_file ['csv', 'tsv'] (default 'csv')
    rule_type: str
        Type of reaction rules ['all', 'forward', 'retro'] (default 'all')
    radii: Sequence[int]
        Integer radii to keep (default 0–10). Expressions are expanded before this call.
    ecx: List[str]
        List of EC numbers to remove from rules
    ec: List[str]
        List of EC numbers to only keep in rules
    output_format: str
        Format of file results are written into
    logger : Logger
        The logger object.
    release: str
        RetroRules version (default 3.1.0), rr02, or latest.
    dataset: str
        Dataset name, comma/plus-separated names, or all (default metanetx).

    Returns
    -------
    None or str If outfile is None, returns the resulting csv format as a string. Otherwise returns None..

    """

    radii, sep, quoting = check_args(rule_type, radii, input_format, output_format)

    rules_files = [rules_file]
    if rules_file == "retrorules":
        rules_files = fetch_datasets(rules_dir, release, dataset)
        sep = ","

    logger.debug("Reading values...")
    # Read 'csv' as 'tsv' by specying separator
    read_options = {
        "sep": sep,
        "dtype": {"RADII": str, "ECS": str, "EC number": str},
        "float_precision": "round_trip",
    }
    frames = [_read_rules(filename, **read_options) for filename in rules_files]
    rf = _merge_templates(frames) if len(frames) > 1 else frames[0]

    # Filter rules according to rule usage and normalized radii.
    templates = "TEMPLATE_ID" in rf.columns
    if templates:
        rf = rf.rename(
            columns={
                "TEMPLATE_ID": "Rule ID",
                "TEMPLATE": "Rule",
                "ECS": "EC number",
                "SCORE": "Score",
            }
        )
    results = filter_(rf, rule_type, radii, ecx, ec, logger=logger)

    # If 'rules_scores_file' is set, then read it and merge with 'results'
    if scores_file:
        logger.debug("Reading scores values...")
        rsf = read_csv(scores_file, sep=sep, float_precision="round_trip")
        results = replace_scores(results, rsf, logger=logger)

    logger.info("Writing results...")
    return results.to_csv(
        outfile,
        index=False,
        sep=("," if output_format == "csv" else "\t") if templates else sep,
        **({} if templates else {"quoting": quoting}),
    )


def replace_scores(results, scores, logger: Logger = LOGGER):
    """
    Replace scores in 'results' with those in 'rules_scores_file'.

    Parameters
    ----------
    results: DataFrame
        DataFrame containing the results

    scores: DataFrame
        DataFrame containing the Rule IDs and the scores to replace

    logger : Logger
        The logger object.
    """
    # Replace scores in results with those in 'rules_scores_file' for the same rules
    logger.debug("Merging scores with rules...")
    # Create a mapping from df2
    score_map = scores.set_index("Rule ID")["Score"]
    # Update the Score in df1 if Rule ID is in df2
    results = results.copy()
    # warning if Rule ID has been found
    # in scores but not in results
    missing_rules = set(scores["Rule ID"]) - set(results["Rule ID"])
    if missing_rules:
        logger.warning(
            f"Rule IDs {missing_rules} found in scores file but not in results. "
            "Its score will not be used."
        )
    # Update the Score in results DataFrame
    # using the mapping from scores
    results["Score"] = results["Rule ID"].map(score_map).fillna(results["Score"])
    results.loc[:, "Score"] = results["Rule ID"].map(score_map).fillna(results["Score"])
    # # Optional: convert Score back to the original dtype if needed
    # results['Score'] = results['Score'].astype(float)
    return results


def filter_(
    df: DataFrame,
    rule_type: str,
    radii: list[int],
    ecx: list[str] | None = None,
    ec: list[str] | None = None,
    logger: Logger = LOGGER,
) -> DataFrame:
    """
    Filter a pandas dataframe using radii and rule usage.

    Parameters
    ----------
    df: DataFrame
        Pandas dataframe
    rule_type: str
        Type of reaction rules ['all', 'forward', 'retro']
    radii: List[int]
        Radii to filter
    ecx: List[str]
        List of EC numbers to filter out from rules
    ec: List[str]
        List of EC numbers to only keep in rules
    logger : Logger
        The logger object.

    Returns
    -------
    query: Pandas dataframe
        Original dataframe filtered by rule usage and radii.
    """
    logger.debug(f"Args: {df}, {rule_type}, {radii}")

    ecx = ecx if ecx is not None else []
    ec = ec if ec is not None else []
    ec_filter = ecx if ecx else ec
    filter = "in" if ec else "not in"
    logger.info("Filtering rules:")
    logger.info(f" -> EC numbers ({filter}): {ec_filter}")
    logger.info(f" -> Radii: {radii}")
    logger.info(f" -> Rule types: {rule_type}")

    # Identify rules that contain at least one EC number starting by a pattern contained in 'ecx'
    rules_idx = filter_rules_by_ec(df, ec_filter, logger)

    # Build the filtering query
    query = f"index {filter} @rules_idx"
    query_vars = {
        "rules_idx": rules_idx,
        "radii": radii,
        "rule_usage_filter": ["both", rule_type],
    }
    if "RADII" in df.columns:
        if rule_type != "all":
            raise ValueError(
                "RetroRules templates have no retro/forward annotation; use --rule-type all"
            )
        radius_idx = df[
            df["RADII"]
            .fillna("")
            .astype(str)
            .apply(
                lambda values: any(
                    int(radius) in radii for radius in values.split(";") if radius
                )
            )
        ].index
        query_vars["radius_idx"] = radius_idx
        query += " & index in @radius_idx"
    else:
        query_vars["diameters"] = [2 * radius for radius in radii]
        query += " & Diameter == @diameters"
    if rule_type != "all":
        query += " & `Rule usage` == @rule_usage_filter"
    logger.debug(f"Query: {query}")
    try:
        _df = df.query(query, local_dict=query_vars)
        logger.info("")
        logger.info(f"=> {len(_df)} rules found")
        logger.info("")
        return _df
    except (KeyError, TypeError, ValueError) as e:
        raise KeyError(e) from e


def filter_rules_by_ec(
    df: DataFrame, ec_filter: list[str], logger: Logger = LOGGER
) -> list[int]:
    """
    Filter out rules that contain at least one EC number that starts with one in 'ecx'.

    Parameters
    ----------
    df: DataFrame
        Pandas dataframe
    ec: List[str]
        List of EC numbers to filter
    logger : Logger
        The logger object.
    """
    # Consider EC numbers as list (separator: ';')
    ec_numbers = df["EC number"].fillna("").str.split(";")

    # Find indices of rows where any EC number starts with one in 'ec_filter'
    def filter_ec_numbers(ec_list, ec_filter):
        return any(any(ec.startswith(ec_f) for ec_f in ec_filter) for ec in ec_list)

    # Apply filtering function and get indices
    rules_idx = df[
        ec_numbers.apply(lambda x: filter_ec_numbers(x, ec_filter))
    ].index.tolist()

    # Debug log
    if logger.level == 10:
        for i in rules_idx:
            logger.debug(
                f"Tagging rule {i} with EC numbers {df.at[i, 'EC number']} because an EC number appears in the exclusion filter"
            )

    # # Remove rules that contain at least one EC number that starts with one in 'ecx',
    # # e.g. rule with EC numbers = ['1.1.1.1', '2.2.2.2'] will be removed if 'ecx' contains '1.1'
    # rules_idx = []
    # for i, ec in enumerate(ec_numbers):
    #     for ec_filter_elt in ec_filter:
    #         if any([ec.startswith(ec_filter_elt) for ec in ec]):
    #             rules_idx.append(i)
    #             logger.debug('Tagging rule {i} with EC numbers {ec} because \'{ec_f_elt}\' appear in the exclusion filter'.format(i=i, ec=ec, ec_f_elt=ec_filter_elt))
    #             break
    return rules_idx


def fetch_retrorules(
    rules_dir: str = DEFAULT_RULES_DIR,
    logger: Logger = LOGGER,
    release: str = DEFAULT_RELEASE,
    dataset: str = "metanetx",
) -> str:
    """
    Fetch RetroRules over Internet if not already on disk.

    Parameters
    ----------
    rules_dir: str
        Directory where to cache RetroRules source files.
    logger : Logger
        The logger object.

    Returns
    -------
    filename: str
        Path to downoaded filename.
    """
    return fetch_dataset(rules_dir, release, dataset)


def check_args(
    rule_type: str,
    radii: Sequence[int],
    input_format: str,
    output_format: str,
    logger: Logger = LOGGER,
) -> tuple[list[int], str, int]:
    """
    Check arguments are well-formed and format them.

    Parameters
    ----------
    rule_type: str
        Type of reaction rules ['all', 'forward', 'retro'] (default 'all')
    radii: Sequence[int]
        Integer radii to keep (default 0–10). Expressions are expanded before this call.
    input_format: str
        Input format of rules_file ['csv', 'tsv'] (default 'csv')
    output_format: str
        Format of file results are written into
    logger : Logger
        The logger object.

    Returns
    -------
    radii, sep, quoting: Tuple[List[int], str, int]
        radii - validated integer radii.
        sep - separation character detected from 'input_format'.
        quoting - quoting behavior detected from 'output_format'.
    """
    logger.debug(f"Args: {rule_type}, {radii}, {input_format}, {output_format}")

    # Rule type
    if not rule_type or rule_type not in ["all", "retro", "forward"]:
        raise ValueError("Cannot detect 'rule_type' input: " + str(rule_type))

    if isinstance(radii, (str, bytes)) or not isinstance(radii, Sequence):
        raise TypeError(
            "radii must be a sequence of integers from 0 to 10; expand expressions with parse_radii()"
        )
    if any(type(radius) is not int or not 0 <= radius <= 10 for radius in radii):
        raise ValueError("Radii must be integers from 0 to 10")
    radii = sorted(set(radii))

    # Input format
    if input_format == "csv":
        sep = ","
    elif input_format == "tsv":
        sep = "\t"
    else:
        raise ValueError("Can only have 'csv' or 'tsv' input formats")

    # Output format
    if output_format == "csv":
        quoting = QUOTE_NONE
    elif output_format == "tsv":
        quoting = QUOTE_ALL
    else:
        raise ValueError("Can only have 'csv' or 'tsv' input formats")

    return radii, sep, quoting
