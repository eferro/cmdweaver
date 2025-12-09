import shlex


class Parser:
    def parse(self, input_line: str) -> list[str]:
        tokens = shlex.split(input_line)
        if input_line.endswith(" "):
            tokens.append("")
        return tokens
