#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
UnitTest parser
"""

import xml.etree.ElementTree
import time


class UnitTestParser(object):
	""" UnitTest parser """

	HEADER_KEY = ['tests', 'failures', 'errors', 'skip']
	TESTCASE_COL = ['classfile', 'classname', 'name', 'time']

	TESTCASE_MAIN_COLORS = {\
		'failure' : 'bg-danger',
		'error' : 'bg-warning'}

	TESTCASE_CHILD_COLORS = {\
		'failure' : 'bg-danger',
		'error' : 'bg-warning',
		'system-out' : 'bg-light',
		'system-err' : 'bg-light'}

	AUTHOR_NAME = 'happy.sources'
	AUTHOR_URL = 'https://github.com/happysources'


	def parse(self, xmlfile):
		""" xml parser """

		tree = xml.etree.ElementTree.parse(xmlfile)
		root = tree.getroot()

		xmlstruct = {'head':root, 'data':[], 'time':{'total':0.0}, 'classnames':{}}
		for child in root:

			# time
			xmlstruct['time']['total'] = xmlstruct['time']['total'] + float(child.attrib['time'])

			classname = child.attrib['classname']
			classnames = classname.split('.')
			xmlstruct['time'][classname] = xmlstruct['time'].get(classname, 0.0)
			xmlstruct['time'][classname] = xmlstruct['time'][classname] + float(child.attrib['time'])
			# classnames
			xmlstruct['classnames'][classname] = xmlstruct['classnames'].get(classname, 0)
			xmlstruct['classnames'][classname] = xmlstruct['classnames'][classname] + 1

			# class file/name
			child.attrib['classfile'] = classnames[0]
			child.attrib['classname'] = classnames[1]

			# testcase
			struct = {'tag': child.tag, 'attrib':child.attrib, 'child':[]}

			for subchild in child:

				struct['child'].append({\
					'tag': subchild.tag,\
					'attrib': subchild.attrib,
					'text': subchild.text})

			xmlstruct['data'].append(struct)

		return xmlstruct


	def __header(self, xmlstruct):
		""" header """

		# header: html
		output = []
		output.append('<html>')
		output.append('\t<head>')
		output.append('\t\t<meta charset="UTF-8">')
		output.append('\t\t<meta name="author" content="%s" />' % self.AUTHOR_NAME)
		output.append('\t\t<meta http-equiv=”last-modified” content=”%s”>' % \
			time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
		output.append('\t\t<link rel="stylesheet" ')
		output.append('href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" ')
		output.append('crossorigin="anonymous">')
		output.append('\t</head>')
		output.append('</body>')

		# header
		output.append('<h1>Test Result</h1>')

		# header: attrib
		for attribName in self.HEADER_KEY:
			output.append('\t<strong>%s</strong>: %s<br />' % \
				(attribName, xmlstruct['head'].attrib[attribName]))

		# header: classname
		classnames = xmlstruct['classnames']
		output.append('\t<strong>classname</strong>: <br /> ')
		for className in classnames:
			output.append('- %s: %s <br />' % \
				(className, classnames[className]))

		# header: time
		output.append('\t<strong>time</strong>: <br />')
		for timeName in xmlstruct['time']:
			output.append('- %s: %s <br />' % \
				(timeName, xmlstruct['time'][timeName]))

		return output


	def __footer(self, output):
		""" footer """

		output.append('<hr size=1>')
		output.append('<div class="float-right">developed with love <a href="%s">%s</a></div>' % \
			(self.AUTHOR_URL, self.AUTHOR_NAME))

		output.append('</body></html>')

		return output


	def html(self, xmlstruct):
		""" generate html code """

		# header
		output = self.__header(xmlstruct)

		# testcase results
		output.append('<table class="table">')

		output.append('<thead>')
		output.append('<tr>')
		#output.append('\t<th scope="col">Tag</td>')
		for colname in self.TESTCASE_COL:
			output.append('\t<th scope="col">%s</td>' % colname)
		output.append('</tr>')
		output.append('</thead>')

		output.append('<tbody>')

		# data / content
		output = self.__data(output, xmlstruct['data'])

		output.append('</tbody>')
		output.append('</table>')

		# footer
		output = self.__footer(output)

		return '\n'.join(output)


	def __dataColor(self, child):
		""" line color """

		bgcolor = 'bg-success'
		for subline in child:
			if subline['tag'] in self.TESTCASE_MAIN_COLORS:
				bgcolor = self.TESTCASE_MAIN_COLORS[subline['tag']]

		return bgcolor


	def __data(self, output, data):
		""" data / content from testcase """

		for line in data:

			bgcolor = self.__dataColor(line['child'])

			output.append('<tr class="%s">' % bgcolor)
			#output.append('\t<td>%s</td>' % line['tag'])
			for key in self.TESTCASE_COL:
				output.append('\t<td>%s</td>' % (line['attrib'][key]))

			output.append('</tr>')

			# subtag child
			output = self.__child(output, line)

		return output


	def __child(self, output, line):
		""" subtag child from testcase """

		for subline in line['child']:

			bgcolor = self.TESTCASE_CHILD_COLORS.get(subline['tag'], 'bg-white')

			output.append('<tr class="%s">' % bgcolor)
			output.append('\t<td> &nbsp; </td>')
			output.append('\t<td colspan=3>%s:<br />' % subline['tag'])
			output.append('\t<textarea class="form-control" rows=5>%s</textarea></td>' % subline['text'])
			output.append('</tr>')

			if subline['attrib']:

				output.append('<tr class="%s">' % bgcolor)
				output.append('\t<td> &nbsp; </td>')
				output.append('\t<td colspan=3>%s:<br />' % subline['attrib']['type'])
				output.append('\t<textarea class="form-control" rows=5>%s</textarea></td>' % \
					subline['attrib']['message'])
				output.append('</tr>')

		return output



if __name__ == '__main__':

	import sys

	XML_FILE = sys.argv[1]

	P = UnitTestParser()
	XML_STRUCT = P.parse(XML_FILE)
	print(P.html(XML_STRUCT))
