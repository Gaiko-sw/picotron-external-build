import argparse
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime as Datetime
import re

@dataclass
class Args:
	output_directory: Path
	input_cart: Path

class PodInfo:
	pod_format: str
	created: Datetime
	modified: Datetime
	revision: int

def main(args: Args):
	if args.output_directory.is_file():
		raise Exception("Input directory was not dir")

	if not args.output_directory.is_dir():
		args.output_directory.mkdir()

	if not args.input_cart.is_file():
		if not (args.input_cart.with_suffix(".p64").is_file()):
			raise Exception("Input cart was not cart")

	with open(args.input_cart) as f:
		cart_content = f.read()

	pattern = re.compile(r":: (.*\.lua)", flags=re.DOTALL)

	first_code_line = None
	last_code_line = None
	in_file = False
	file_name = None
	lines = cart_content.splitlines()
	out_content: str = ""
	i = 0
	while (line := lines[i]) != ":: [eoc]":
		if not in_file:
			# begin file
			if match := pattern.match(line):
				if not first_code_line:
					first_code_line = i
				in_file = True
				file_name = match.group(1)
				i += 1
				out_content = lines[i] + "\n"
			i += 1
			continue

		elif in_file:
			match = pattern.match(line)
			if not match:
				match = re.match(r":: .info.pod", line)
			if match:
				# end this file
				print(f"Writing {file_name}")
				with open(args.output_directory / file_name, "w") as f:
					f.write(out_content)
				in_file = False
				# continue without advancing line
				continue

			else:
				out_content += line + "\n"
				last_code_line = i
				i += 1
				continue

	skel_cart_content = "\n".join(lines[0:first_code_line])
	skel_cart_content += "\n\n\n:: main.lua\n@@code\n\n"
	skel_cart_content += "\n".join(lines[last_code_line:-1])
	skel_cart_name = Path(args.input_cart.stem + "_skel.p64")
	print(f"Writing {skel_cart_name}")
	with open(args.output_directory / skel_cart_name, "w") as f:
		f.write(skel_cart_content)

	print(f"Finished writing lua files & p64 to {args.output_directory}")
	
def get_pod_info(line: str) -> PodInfo:
	if line[0:4] != "--[[":
		raise Exception(f"No content")
	
	date_format = "%Y-%m-%d %H:%M:%S"

	ret = PodInfo()
	
	m = re.search(r"pod_format=\"(.*?)\"", line).group(1)
	ret.pod_format = m

	m = re.search(r"created=\"(.*?)\"", line).group(1)
	ret.created = Datetime.strptime(m, date_format)

	m = re.search(r"modified=\"(.*?)\"", line).group(1)
	ret.modified = Datetime.strptime(m, date_format)

	m = re.search(r"revision=(\d*?)]", line).group(1)
	ret.revision = int(m)

	return ret
	

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description="Picotron cart code exporter"
	)
	parser.add_argument('input_cart', type=Path, help="Original picotron cart")
	parser.add_argument('output_directory', type=Path, help="Directory containing lua files to compile into Picotron cartridge")
	
	args = parser.parse_args()
	main(Args(
		output_directory=args.output_directory,
		input_cart=args.input_cart,
	))
	




	