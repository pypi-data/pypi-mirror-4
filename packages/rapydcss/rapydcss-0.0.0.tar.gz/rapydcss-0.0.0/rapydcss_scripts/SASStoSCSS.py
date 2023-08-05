import sys, os


def parse_file(input_file_name, output_file):
	state = {
		'indent_marker':0,
		'prev_indent':	0,
		'prev_line':	'',
		'nested_blocks':0,
		'line_buffer':	'',
	}
	
	# create a separate funtion for parsing the line so that we can call it again after the loop terminates
	def parse_line(line, state):
		line = state['line_buffer'] + line.rstrip() # remove EOL character
		if line and line[-1] == '\\':
			state['line_buffer'] = line[:-1]
			return
		else:
			state['line_buffer'] = ''
		
		indent = len(line) - len(line.lstrip())
	
		# make sure we support multi-space indent as long as indent is consistent
		if indent and not state['indent_marker']:
			state['indent_marker'] = indent
	
		if state['indent_marker']:
			indent /= state['indent_marker']
	
		if indent == state['prev_indent']:
			# same indentation as previous line
			if state['prev_line']:
				state['prev_line'] += ';'
		elif indent > state['prev_indent']:
			# new indentation is greater than previous, we just entered a new block
			state['prev_line'] += ' {'
			state['nested_blocks'] += 1
		else:
			# indentation is reset, we exited a block
			block_diff = state['prev_indent'] - indent
			if state['prev_line']:
				state['prev_line'] += ';'
			state['prev_line'] += ' }' * block_diff
			state['nested_blocks'] -= block_diff
		output_file.write(state['prev_line'] + '\n')
		state['prev_indent'] = indent
		state['prev_line'] = line
	
	with open(input_file_name, 'r') as input_file:
		for input_line in input_file:
			parse_line(input_line, state)
		parse_line('\n', state) # parse the last line stored in prev_line buffer
		

if __name__ == "__main__":
	orig_dir = os.getcwd()
	base_dir, orig_file = os.path.split(sys.argv[1])
	filename = orig_file.rsplit('.', 1)[0] # remove the extension

	if base_dir:
		os.chdir(base_dir)
	
	with open(filename+'.scss', 'w') as output:
		parse_file(orig_file, output)
