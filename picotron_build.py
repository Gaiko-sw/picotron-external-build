import argparse
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta
import platform
import os
import re

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

@dataclass
class Args:
    input_directory: Path
    input_skel: Path
    output_cart: Path

def main(args: Args):
    if not args.input_directory.is_dir():
        raise Exception("Input directory was not dir")

    if not args.input_skel.is_file():
        if not (args.input_skel.with_suffix(".p64").is_file()):
            raise Exception("Input cart was not cart")
        
    args.output_cart = args.output_cart.with_suffix(".p64")

    with open(args.input_skel) as f:
        cart_content = f.read()

    if not (match := re.search(":: main.lua\n@@code", cart_content)):
        raise Exception("Input skel file didn't contain @@code tag")
    
    code_content = ""
    for file in [f for f in args.input_directory.iterdir() if f.suffix == ".lua"]:
        print(f"Processing {file}", end="")
        sys_mod_time = file.stat().st_mtime
        sys_mod_time = datetime.fromtimestamp(sys_mod_time).replace(microsecond=0)
        create_time = (
            file.stat().st_ctime 
            if platform.system() == "Windows"
            else os.path.getctime(file)
        )
        create_time = datetime.fromtimestamp(create_time).replace(microsecond=0)
        with open(file, 'r') as f:
            lines = f.readlines()

        pod_line = lines[0]

        # create pod line (assuming it's a new file)
        if pod_line[0:4] != "--[[":
            print("\tCREATING pod line", end="")
            new_pod_line = f'--[[pod_format="raw",created="{create_time}",modified="{sys_mod_time}",revision=1]]\n\n'

            lines.insert(0, new_pod_line)
            lines.insert(1, f"-- {file.name}")

            with open(file, "w") as f:
                f.writelines(lines)
        else:
            if new_line := modify_pod_line(pod_line, sys_mod_time):
                print("\tModifying pod line", end="")
                lines[0] = new_line

                with open(file, 'w') as f:
                    f.writelines(lines)

        code_content += f":: {file.name}\n"
        code_content += "".join(lines)
        code_content += "\n\n"

        print()

    print(f"Writing {args.output_cart}")
    out_content = cart_content.replace(':: main.lua\n@@code', code_content)
    with open(args.output_cart, 'w') as f:
        f.write(out_content)

    print(f"Finished writing {args.output_cart}")


"""
Returns 
Optional[str] modified pod_line if the file's mod stamp on disk is newer, else None
"""
def modify_pod_line(pod_line: str, sys_mod_time: datetime) -> str:
    pod_mod_time = re.search(r"modified=\"(.*?)\"", pod_line).group(1)
    pod_mod_time = datetime.strptime(pod_mod_time, DATE_FORMAT)

    # modify pod
    print()
    print(f"{sys_mod_time} : {pod_mod_time}")
    if sys_mod_time > (pod_mod_time + timedelta(seconds=10)):
        new_pod_line = pod_line

        new_pod_line = re.sub(r"modified=\"(.*?)\"", f'modified="{sys_mod_time}"', new_pod_line)

        revision = re.search(r"revision=(\d*)", new_pod_line).group(1)
        new_revision = int(revision) + 1
        new_pod_line = re.sub(r"revision=(\d*)", f"revision={new_revision}", new_pod_line)

        return new_pod_line

    else:
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Picotron cartridge compiler"
    )
    parser.add_argument('input_directory', type=Path, help="Directory containing lua source files to compile into Picotron cartridge")
    parser.add_argument('input_skel', type=Path, help="Picotron skeleton cart, with @@code annotation, from picotron_export.py (not the original Picotron cart)")
    parser.add_argument('output_cart', type=Path, help="Name of file to output")
    args = parser.parse_args()

    if not args.input_skel:
        input_skel = args.input_directory / "skel.p64"
    else:
        input_skel = args.input_skel

    if not args.output_cart:
        output_cart = args.input_directory / "out.p64"
    else:
        output_cart = args.output_cart

    main(Args(
        input_directory=args.input_directory,
        input_skel=args.input_skel,
        output_cart=output_cart,

    ))
    




	