import argparse
from pathlib import Path
import pandas as pd
import rich
import sys

DEFAULT_OUT_FILEPATH = Path(__file__).resolve().parent / "contacts.vcf"

parser = argparse.ArgumentParser(description="Generates a contacts.vcf file from input csv file")

parser.add_argument("input", help="csv file path", type=Path)
parser.add_argument(
    "--name",
    help="columns to combine when writing names (e.g. 'first name' 'last name')",
    nargs="+",
)
parser.add_argument(
    "--phone", help="column which stores phone number (default second column)"
)
parser.add_argument(
    "-o", "--output", help="out file path", type=Path, default=DEFAULT_OUT_FILEPATH
)

args = parser.parse_args()
if not args.input.exists():
    rich.print("[red]The input file path does not exist.")
    sys.exit(1)


df = pd.read_csv(args.input)
df.columns = [col.lower().strip() for col in df.columns]

names_found = True
if args.name is not None:
    for i, name in enumerate(args.name):
        args.name[i] = args.name[i].lower().strip()
        if args.name[i] not in df.columns:
            rich.print(f"[red] Name column '{name}' not present in csv file")
            names_found = False

if not names_found:
    sys.exit(2)

if args.phone is not None and args.phone not in df.columns:
    rich.print(f"[red] Phone column '{args.phone}' not found in csv file")
    sys.exit(3)

with open(args.output, "w") as vcf_file:
    # Iterate over each row in the DataFrame
    for _, row in df.iterrows():
        if args.name:
            name = " ".join(row[name_col].strip() for name_col in args.name)
        else:
            name = row.iloc[0]
        if args.phone:
            phone = row[args.phone]
        else:
            phone = row.iloc[1]

        # Write the vCard entry
        vcf_file.write("BEGIN:VCARD\n")
        vcf_file.write("VERSION:3.0\n")
        vcf_file.write(f"N:{name.title()}\n")
        vcf_file.write(f"TEL;TYPE=CELL:{phone}\n")
        vcf_file.write("END:VCARD\n\n")

rich.print(f"[green]File '{args.output}' written sucessfully.")
