# -*- coding:utf-8 -*-

import sys
import argparse

class Node(object):
	def __init__(self, **attrs):
		self.__dict__.update(attrs)

	def __str__(self):
		return ' ' * self.indent + self.text + '\n' + '\n'.join(map(str, self.children))

	def is_root(self):
		return not bool(self.parent)

	def graphviz(self):
		if not self.children:
			return ''
		buff = []
		for child in self.children:
			buff.append('"%s"--"%s";' %(self.text, child.text))
			buff.append(child.graphviz())
		return '\n'.join(buff)

class Error(StandardError):
	pass

def parse_args():
	parser = argparse.ArgumentParser()

	parser.add_argument("-i", "--infile", default = "",
		help = "If no input files are supplied, the program reads from stdin. ")

	parser.add_argument("-o", "--outfile", default = "",
		help = "Write output to file outfile. By default, output goes to stdout. ")

	args = parser.parse_args()
	return args

def indent_length(line):
	for i in xrange(len(line)):
		a = line[i]
		if a != ' ' and a != '\t':
			return i
	return len(line)

def convert(ibmm_fd, gv_fd):
	tree = parse_file(ibmm_fd)
	template = """
		graph {
			%s
		}
		""" % tree.graphviz()
	print template


def parse_file(fd):
	root = None
	line_num = 0
	for line in fd:
		line_num += 1
#		print line
#		print '*' * 30
#		print str(root)
#		print '*' * 30
		
		t = line.rstrip()
		if not t:
			continue
		if root is None:
			prev_indent = indent_length(line)
			prev_node = root = Node(text = line.strip(),
				parent = None,
				children = [],
				indent = prev_indent,
				)
			continue
		curr_indent = indent_length(line)
		# brother
		if curr_indent == prev_indent:
			prev_node.parent.children.append(Node(text = line.strip(),
				parent = prev_node.parent,
				children = [],
				indent = curr_indent,
				))
		# child
		elif curr_indent > prev_indent:
			curr_node = Node(text = line.strip(),
				parent = prev_node,
				children = [],
				indent = curr_indent,
				)
			prev_node.children.append(curr_node)
			prev_indent = curr_indent
			prev_node = curr_node
		# uncle, grantuncle, grantgrantuncle...
		elif curr_indent < prev_indent:
			t = prev_node
			while True:
				grantparent = t.parent
				if grantparent is None:
					raise Error('invalid indent. line %d' % line_num)
				if curr_indent < grantparent.indent:
					t = grantparent
					continue
				elif curr_indent == grantparent.indent:
					if grantparent.parent is None:
						raise Error('invalid indent. line %d' % line_num)
					prev_node = grantparent.parent
					break
				else:
					raise Error('invalid indent. line %d' % line_num)
			curr_node = Node(text = line.strip(),
				parent = prev_node,
				children = [],
				indent = curr_indent,
				)
			prev_node.children.append(curr_node)
			prev_indent = curr_indent
			prev_node = curr_node
		else:
			raise Error('invalid indent. line %d' % line_num)
		
	return root

def main():
	args = parse_args()
	if args.infile:
		ibmm_fd = open(args.infile, 'rt')
	else:
		ibmm_fd = sys.stdin

	if args.outfile:
		gv_fd = open(args.outfile, 'wt')
	else:
		gv_fd = sys.stdout

	convert(ibmm_fd, gv_fd)

#	print 'infile = ', args.infile
#	print 'outfile = ', args.outfile
#	print 'format = ', args.format
