# -*- coding: utf-8 -*-

# Copyright 2013 Vincent Jacques
# vincent@vincent-jacques.net

# This file is part of RecursiveDocument. http://jacquev6.github.com/RecursiveDocument

# RecursiveDocument is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# RecursiveDocument is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License along with RecursiveDocument.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import textwrap

from recdoc import Document, Section, DefinitionList


class DefinitionListTestCase(unittest.TestCase):
    __shortLorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque facilisis nisi vel nibh"

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.maxDiff = None
        self.doc = Document()

    def testDefinitionList(self):
        self.doc.add(
            DefinitionList()
            .add("Item 1", "Definition 1")
            .add("Item 2", "Definition 2")
        )
        self.assertEqual(
            self.doc.format(),
            textwrap.dedent(
                """\
                Item 1  Definition 1
                Item 2  Definition 2
                """
            )
        )

    def testItemsWithDifferentLengths(self):
        self.doc.add(
            DefinitionList()
            .add("Item 1", "Definition 1")
            .add("Longer item 2", "Definition 2")
        )
        self.assertEqual(
            self.doc.format(),
            textwrap.dedent(
                """\
                Item 1         Definition 1
                Longer item 2  Definition 2
                """
            )
        )

    def testWithinSubSection(self):
        self.doc.add(
            Section("Section")
            .add(
                Section("Sub-section")
                .add(
                    DefinitionList()
                    .add("Item 1", "Definition 1")
                    .add("Longer item 2", "Definition 2")
                )
            )
        )
        self.assertEqual(
            self.doc.format(),
            textwrap.dedent(
                """\
                Section:
                  Sub-section:
                    Item 1         Definition 1
                    Longer item 2  Definition 2
                """
            )
        )

    def testEmptyDefinition(self):
        self.doc.add(
            DefinitionList()
            .add("Longer item 1", "Definition 1")
            .add("Item 2", "")
            .add("Longer item 3", "")
        )
        self.assertEqual(
            self.doc.format(),
            textwrap.dedent(
                """\
                Longer item 1  Definition 1
                Item 2
                Longer item 3
                """
            )
        )

    def testWrappingOfDefinitionWithOnlyShortItems(self):
        self.doc.add(
            Section("Section")
            .add(
                DefinitionList()
                .add("Item 1 (short enought)", "Definition 1 " + self.__shortLorem)
                .add("Item 2", "Definition 2 " + self.__shortLorem)
            )
        )
        self.assertEqual(
            self.doc.format(),
            textwrap.dedent(
                # 70 chars ###########################################################
                """\
                Section:
                  Item 1 (short enought)  Definition 1 Lorem ipsum dolor sit amet,
                                          consectetur adipiscing elit. Pellentesque
                                          facilisis nisi vel nibh
                  Item 2                  Definition 2 Lorem ipsum dolor sit amet,
                                          consectetur adipiscing elit. Pellentesque
                                          facilisis nisi vel nibh
                """
            )
        )

    def testWrappingOfDefinitionWithShortAndLongItems(self):
        self.doc.add(
            Section("Section")
            .add(
                DefinitionList()
                .add("Item 1 (just tooo long)", "Definition 1 " + self.__shortLorem)
                .add("Item 2", "Definition 2 " + self.__shortLorem)
            )
        )
        self.assertEqual(
            self.doc.format(),
            textwrap.dedent(
                # 70 chars ###########################################################
                """\
                Section:
                  Item 1 (just tooo long)
                          Definition 1 Lorem ipsum dolor sit amet, consectetur
                          adipiscing elit. Pellentesque facilisis nisi vel nibh
                  Item 2  Definition 2 Lorem ipsum dolor sit amet, consectetur
                          adipiscing elit. Pellentesque facilisis nisi vel nibh
                """
            )
        )

    def testWrappingOfDefinitionWithOnlyLongItems(self):
        self.doc.add(
            Section("Section")
            .add(
                DefinitionList()
                .add("Item 1 (just tooo long)", "Definition 1 " + self.__shortLorem)
                .add("Item 2 (also too long, really)", "Definition 2 " + self.__shortLorem)
            )
        )
        self.assertEqual(
            self.doc.format(),
            textwrap.dedent(
                # 70 chars ###########################################################
                """\
                Section:
                  Item 1 (just tooo long)
                    Definition 1 Lorem ipsum dolor sit amet, consectetur adipiscing
                    elit. Pellentesque facilisis nisi vel nibh
                  Item 2 (also too long, really)
                    Definition 2 Lorem ipsum dolor sit amet, consectetur adipiscing
                    elit. Pellentesque facilisis nisi vel nibh
                """
            )
        )
