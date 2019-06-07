import argparse
import json
import os.path
import uuid
import shutil
import zipfile
import pathlib

class GenerateResults():
    """ This function generates a compressed file from a list of files.

    Args:
        config (str): Configuration file in JSON or YAML formats or JSON string.
        input (str): Input folder path.
        output (str): Output file path.

    """

    def __init__(self, config, input, output, **kwargs):
        self.config = self.read_config(config)
        self.input = input
        self.output = output

        self.check_io()

    def read_config(self, config):
        """ Checks if config is a JSON / YAML file or a JSON string and returns it parsed """
        try:
            config_file = os.path.abspath(config)
            with open(config_file, 'r') as stream:
                if config_file.lower().endswith((".yaml",".yml")):
                    return yaml.safe_load(stream)
                else:
                    return json.load(stream)
        except:
            return json.loads(config)

    def check_io(self):
        """ Checks the input and output paths """
        # Check input
        if not os.path.exists(self.input):
            raise SystemExit('Unexisting input directory. Exiting.')
        # Check output
        if os.path.dirname(self.output) and not os.path.exists(os.path.dirname(self.output)):
            raise SystemExit('Unexisting output directory. Exiting.')

    def create_unique_dir(self, prefix='', number_attempts=10):
        """Create a directory with a prefix + computed unique name."""
        name = prefix + str(uuid.uuid4())
        for i in range(number_attempts):
            try:
                os.mkdir(name)
                print('%s directory successfully created' %(name))
                return name
            except FileExistsError:
                print(name + ' Already exists')
                print('Retrying %i times more' %(number_attempts-i))
                name = prefix + str(uuid.uuid4())
                print('Trying with: ' + name)
        raise FileExistsError

    def parse_config(self):
        """ Parse all config structure and copy all files to tmp_folder with new names"""
        for folder in self.config:
            path = os.path.join(self.input, folder)
            if os.path.exists(path):
                for file in self.config[folder]:
                    src_file = os.path.join(path, file['src'])
                    if os.path.exists(src_file):
                        dst_file = os.path.join(self.tmp_folder, file['dst'])
                        shutil.copy(src_file, dst_file)
                        self.files_list.append(dst_file)

    def zip_list(self, zip_file, file_list, out_log=None):
        """ Compress all files listed in **file_list** into **zip_file** zip file."""
        file_list.sort()
        with zipfile.ZipFile(zip_file, 'w') as zip_f:
            for f in file_list:
                zip_f.write(f, arcname=os.path.basename(f))
        print("Adding:")
        print(str(file_list))
        print("to: "+ os.path.abspath(zip_file))

    def rm(self, file_name):
        file_path = pathlib.Path(file_name)
        try:
            if file_path.exists():
                if file_path.is_dir():
                    shutil.rmtree(file_name)
                    return file_name
                if file_path.is_file():
                    os.remove(file_name)
                    return file_name
        except:
            # Giving the file system some time to consolidate
            time.sleep(2)
            if file_path.exists():
                if file_path.is_dir():
                    shutil.rmtree(file_name)
                    return file_name
                if file_path.is_file():
                    os.remove(file_name)
                    return file_name
        return None

    def launch(self):

        # create temporal folder
        self.tmp_folder = self.create_unique_dir()

        # parse config and copy files to tmp_folder
        self.files_list = []
        self.parse_config()

        # generate compressed file
        self.zip_list(self.output, self.files_list)

        # remove temporary folder
        self.rm(self.tmp_folder)
        print('Removed temporary folder: %s' % self.tmp_folder)

def main():
    parser = argparse.ArgumentParser(description = "Generates a compressed file from a list of files.", formatter_class = lambda prog: argparse.RawTextHelpFormatter(prog, width = 99999))
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('-c', '--config', required = True, help = 'Configuration file in JSON or YAML formats or JSON string.')
    required_args.add_argument('-i', '--input', required = True, help = 'Input folder path.')
    required_args.add_argument('-o', '--output', required = True, help = 'Output file path.')

    args = parser.parse_args()

    GenerateResults(config = args.config, input = args.input, output = args.output).launch()

if __name__ == '__main__':
    main()