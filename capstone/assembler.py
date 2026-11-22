
import re
import sys
from pathlib import Path

SYMBOLS = {
    "SP": 0, "LCL": 1, "ARG": 2,
    "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576
}

for i in range(16):
    SYMBOLS["R" + str(i)] = i

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010",
    "D": "0001100", "A": "0110000", "!D": "0001101",
    "!A": "0110001", "-D": "0001111", "-A": "0110011",
    "D+1": "0011111", "A+1": "0110111",
    "D-1": "0001110", "A-1": "0110010",
    "D+A": "0000010", "D-A": "0010011",
    "A-D": "0000111", "D&A": "0000000",
    "D|A": "0010101",
    "M": "1110000", "!M": "1110001", "-M": "1110011",
    "M+1": "1110111", "M-1": "1110010",
    "D+M": "1000010", "D-M": "1010011",
    "M-D": "1000111", "D&M": "1000000",
    "D|M": "1010101"
}

DEST = {
    "": "000",
    "A": "100",
    "D": "010",
    "M": "001",
    "AD": "110",
    "AM": "101",
    "DM": "011",
    "ADM": "111"
}

JUMP = {
    "": "000", "JGT": "001", "JEQ": "010",
    "JGE": "011", "JLT": "100", "JNE": "101",
    "JLE": "110", "JMP": "111"
}


def valid_symbol(symbol):
    return re.fullmatch(r"[A-Za-z_.$:][A-Za-z0-9_.$:]*", symbol) is not None


def clean_file(filename):
    instructions = []

    with open(filename, "r") as file:
        for number, original in enumerate(file, start=1):
            line = original.split("//")[0]
            line = re.sub(r"\s+", "", line)

            if line:
                instructions.append((number, line))

    return instructions


def first_pass(instructions):
    symbols = SYMBOLS.copy()
    labels = {}
    errors = []
    rom_address = 0
    remaining = []

    for number, line in instructions:
        if line.startswith("(") or line.endswith(")"):
            if not (line.startswith("(") and line.endswith(")")):
                errors.append((number, "Invalid label"))
                continue

            label = line[1:-1]

            if not valid_symbol(label):
                errors.append((number, "Invalid label"))
            elif label in symbols:
                errors.append((number, "Duplicate or reserved label"))
            else:
                symbols[label] = rom_address
                labels[label] = rom_address

        else:
            remaining.append((number, line))
            rom_address += 1

    return remaining, symbols, labels, errors


def second_pass(instructions, symbols):
    output = []
    variables = {}
    errors = []
    next_variable = 16

    for number, line in instructions:
        try:
            if line.startswith("@"):
                symbol = line[1:]

                if not symbol:
                    raise ValueError()

                if symbol.isdigit():
                    address = int(symbol)

                    if address > 32767:
                        raise ValueError()

                else:
                    if not valid_symbol(symbol):
                        raise ValueError()

                    if symbol not in symbols:
                        symbols[symbol] = next_variable
                        variables[symbol] = next_variable
                        next_variable += 1

                    address = symbols[symbol]

                output.append(format(address, "016b"))

            else:
                if line.count("=") > 1 or line.count(";") > 1:
                    raise ValueError()

                if ";" in line:
                    instruction, jump = line.split(";")
                else:
                    instruction, jump = line, ""

                if "=" in instruction:
                    dest, comp = instruction.split("=")
                    dest = "".join(sorted(dest))
                else:
                    dest, comp = "", instruction

                if dest not in DEST or comp not in COMP or jump not in JUMP:
                    raise ValueError()

                binary = "111" + COMP[comp] + DEST[dest] + JUMP[jump]
                output.append(binary)

        except (ValueError, KeyError):
            errors.append((number, "Invalid instruction"))

    return output, variables, errors


def assemble(filename):
    path = Path(filename)

    instructions = clean_file(path)
    instructions, symbols, labels, errors = first_pass(instructions)

    output, variables, second_errors = second_pass(instructions, symbols)
    errors.extend(second_errors)

    if errors:
        for number, message in errors:
            print(f"Line {number}: {message}")

        print("Assembly failed. No .hack file generated.")
        return

    output_file = path.with_suffix(".hack")
    output_file.write_text("\n".join(output) + "\n")

    # Save labels and variables for K = 06
    with open("symbols.txt", "w") as file:
        for name, address in {**labels, **variables}.items():
            file.write(f"{name} {address}\n")

    print("Assembly successful!")
    print("Output:", output_file)
    print("Instructions:", len(output))
    print("Symbols saved to symbols.txt")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assembler.py filename.asm")
    else:
        try:
            assemble(sys.argv[1])
        except OSError as error:
            print("File error:", error)
