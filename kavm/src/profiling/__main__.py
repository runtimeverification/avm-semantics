import os
from argparse import ArgumentParser
from pstats import Stats
from typing import Any, Dict

from pyk.cli_utils import file_path
from tabulate import tabulate


def main() -> None:
    parser = create_argument_parser()
    args = parser.parse_args()
    stats = Stats(str(args.profile_file))
    profiles = stats.get_stats_profile()

    kavm_profiles = []
    for name, func_data in profiles.func_profiles.items():
        func_data.file_name = strip_source_file_path_prefix(func_data.file_name, os.curdir)
        if 'kavm' in func_data.file_name:
            key = (
                strip_source_file_path_prefix(func_data.file_name, os.curdir)
                + f':{func_data.line_number}'
                + f'[{name}]'
            )
            kavm_profiles.append({'function': key, **func_data.__dict__})

    def ncalls_to_int(ncalls_str: str) -> int:
        try:
            return int(ncalls_str)
        except ValueError:
            return int(ncalls_str.split('/')[0])

    sorted_by_ncalls = sorted(kavm_profiles, key=lambda v: ncalls_to_int(v['ncalls']), reverse=True)
    sorted_by_cumtime = sorted(sorted_by_ncalls, key=lambda v: v['percall_cumtime'], reverse=True)

    table: Dict[str, Any] = {'function': [], 'cumtime': [], 'percall_cumtime': [], 'ncalls': []}
    for item in sorted_by_cumtime:
        table['function'].append(item['function'])
        table['percall_cumtime'].append(item['percall_cumtime'])
        table['cumtime'].append(item['cumtime'])
        table['ncalls'].append(item['ncalls'])

    print(tabulate(table, headers=list(table.keys()), tablefmt="github"))


def strip_source_file_path_prefix(path: str, prefix_to_strip: str) -> str:
    return os.path.relpath(path, prefix_to_strip)


def create_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='kavm-profile')

    parser.add_argument('profile_file', type=file_path, help='Path to the .prof file')
    parser.add_argument(
        '--output',
        dest='output',
        type=str,
        help='Output mode',
        choices=['md'],
        default='md',
    )

    return parser


if __name__ == "__main__":
    main()
