"""Remove Metrics' optional Projects achievement without requesting extra token scopes.

This patch targets the pinned dkhokhlov/metrics revision in metrics.yml. It removes
both the Projects V2 query and the Manager achievement calculation: no invented
project counts or badge values are substituted. A source change fails explicitly.
"""
import argparse
from pathlib import Path


PROJECTS_QUERY = """    projectsV2(first: 1, orderBy: {field: CREATED_AT, direction: ASC}) {
      totalCount
      nodes {
        createdAt
        title
      }
    }
"""


def patch(root):
    query_path = root / 'source/plugins/achievements/queries/achievements.graphql'
    users_path = root / 'source/plugins/achievements/list/users.mjs'
    query, users = query_path.read_text(), users_path.read_text()
    if query.count(PROJECTS_QUERY) != 1:
        raise ValueError('Unexpected achievements query; review the pinned Metrics source')
    before, marker, after = users.partition('  //Manager\n')
    manager, reviewer, rest = after.partition('  //Reviewer\n')
    if not marker or not reviewer or 'user.projectsV2' not in manager:
        raise ValueError('Unexpected Manager calculation; review the pinned Metrics source')
    query = query.replace(PROJECTS_QUERY, '', 1)
    users = before + reviewer + rest
    if 'projectsV2' in query or 'user.projectsV2' in users:
        raise ValueError('Projects dependency remains; refusing a partial patch')
    query_path.write_text(query)
    users_path.write_text(users)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    patch(parser.parse_args().source)
    print('Removed the Projects query and Manager achievement; other achievements remain enabled.')
