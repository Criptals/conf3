import argparse
import yaml
import re


class Config:
    def __init__(self):
        self.data = {}

    def add_constant(self, name, value):
        self.data[name] = value

    def to_yaml(self):
        return yaml.dump(self.data, default_flow_style=False)


def remove_multiline_comments(text):
    return re.sub(r'{-.*?-}', '', text, flags=re.DOTALL)


def parse_value(value):
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]  # Удаляем кавычки
    elif value.startswith('[') and value.endswith(']'):
        return [parse_value(v.strip()) for v in value[1:-1].split(',')]
    elif value.startswith('@{') and value.endswith('}'):
        return parse_dict(value[2:-2].strip())
    elif value.isdigit():
        return int(value)
    else:
        return value


def parse_dict(dict_str):
    items = dict_str.split(';')
    result = {}
    for item in items:
        if '=' in item:
            key, value = item.split('=')
            result[key.strip()] = parse_value(value.strip())
    return result


def transform_config(input_text):
    config = Config()
    input_text = remove_multiline_comments(input_text)

    for line in input_text.splitlines():
        line = line.strip()
        if ':=' in line:
            name, value = line.split(':=')
            config.add_constant(name.strip(), parse_value(value.strip()))

    return config


def main():
    parser = argparse.ArgumentParser(description='Transform custom config language to YAML.')
    parser.add_argument('input_file', help='Path to the input configuration file')
    args = parser.parse_args()

    try:
        with open(args.input_file, 'r') as file:
            input_text = file.read()
            config = transform_config(input_text)
            yaml_output = config.to_yaml()
            print(yaml_output)
    except FileNotFoundError:
        print(f"Error: File {args.input_file} not found.")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == '__main__':
    main()
