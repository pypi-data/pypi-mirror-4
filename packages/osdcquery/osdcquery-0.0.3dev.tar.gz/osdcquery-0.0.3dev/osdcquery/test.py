#!/usr/bin/python
from test_query_tool import FakeQuery, FakeFileAssociate, FileMaker


def main():
	# this will be the basic workflow that we will use

	query_maker = FakeQuery()
	
	metadata = query_maker.run_query('test')
	link_builder = FakeFileAssociate()
	links = link_builder.associate(metadata)
	file_maker = FileMaker()
	file_maker.create_links(links)

if __name__ == "__main__":
    main()

