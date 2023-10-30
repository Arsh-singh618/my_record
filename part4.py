import datetime

class FileFormatError(Exception):
    pass

class InvalidDatasetIDError(Exception):
    pass

class InvalidResultError(Exception):
    pass

class Dataset:
    def __init__(self, dataset_id, name, weight, size, source):
        self.dataset_id = dataset_id
        self.name = name
        self.weight = weight
        self.size = size
        self.source = source
        self.type = 'S' if dataset_id[-1] == 'S' else 'A'
        self.average = None
        self.range = None
        self.nfail = None

class Algorithm:
    def __init__(self, name, category, year, authors):
        self.name = name
        self.category = category
        self.year = year
        self.authors = authors
        self.average = 0
        self.nfail = 0
        self.fail_datasets = []
        self.ongoing_results = 0
        self.score = 0

    def compute_statistics(self, results, datasets):
        complete_results = [results.get((self, dataset)) for dataset in datasets if results.get((self, dataset)) not in ('XX', '404', None, '', '--')]
        self.ongoing_results = sum(1 for result in results.values() if result in ('XX', None, '', '--'))
        self.fail_datasets = [f"{dataset.dataset_id} ({results.get((self, dataset))})" for dataset in datasets if results.get((self, dataset)) == '404']
        self.nfail = len(self.fail_datasets)
        # Compute average for complete results
        if complete_results:
            self.average = round(sum(float(result) for result in complete_results) / len(complete_results), 1)

    def satisfies_requirements(self):
        if self.category == 'ML':
            return self.nfail <= 1
        else:
            return self.nfail <= 2

    def __str__(self):
        authors_str = '-'.join(self.authors)
        name = f"{self.name} {'(!)' if not self.satisfies_requirements() else ''}"
        fail_dataset_str = ', '.join(self.fail_datasets)
        return f"| {name:<12} {self.category:<4} {self.year:<4} {authors_str:<20} {self.average:^7.1f} {self.nfail:^5} {fail_dataset_str:<12} {self.ongoing_results:^7} {self.score:^5} |"

class Records:
    def __init__(self):
        self.datasets = []
        self.algorithms = []
        self.results = {}
        self.report_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def add_dataset(self, dataset):
        self.datasets.append(dataset)

    def add_algorithm(self, algorithm):
        self.algorithms.append(algorithm)

    def read_datasets(self, dataset_file_name):
        try:
            with open(dataset_file_name, 'r') as file:
                for line in file:
                    data = line.strip().split(', ')
                    dataset_id, name, weight, size, source = data
                    if not (dataset_id.startswith('D') and dataset_id[-1] in ('S', 'A') and len(dataset_id[1:-1]) == 2 and dataset_id[1:-1].isdigit()):
                        raise InvalidDatasetIDError(f"Invalid dataset ID: {dataset_id}")
                    dataset = Dataset(dataset_id, name, int(weight), int(size), source)
                    self.add_dataset(dataset)
        except FileNotFoundError:
            print(f"File not found: {dataset_file_name}")
            exit()

    def read_algorithms(self, algorithm_file_name):
        try:
            with open(algorithm_file_name, 'r') as file:
                for line in file:
                    data = line.strip().split(', ')
                    name, category, year, *authors = data
                    algorithm = Algorithm(name, category, int(year), authors)
                    self.add_algorithm(algorithm)
        except FileNotFoundError:
            print(f"File not found: {algorithm_file_name}")
            exit()

    def read_results(self, result_file_name):
        try:
            with open(result_file_name, 'r') as file:
                for line in file:
                    data = line.strip().split(', ')
                    algorithm_name = data[0]
                    results = data[1:]
                    if not results:
                        raise FileFormatError("Result file is empty.")
                    for i, result in enumerate(results):
                        dataset_id, result_value = result.split(': ')
                        if dataset_id == '404':
                            result_value = '--'
                        elif not result_value.replace('.', '', 1).isdigit():
                            raise InvalidResultError(f"Invalid result value: {result_value}")
                        dataset = next((ds for ds in self.datasets if ds.dataset_id == dataset_id), None)
                        algorithm = next((alg for alg in self.algorithms if alg.name == algorithm_name), None)
                        if dataset and algorithm:
                            self.results[(algorithm, dataset)] = result_value
        except FileNotFoundError:
            print(f"File not found: {result_file_name}")
            exit()
        except (FileFormatError, InvalidResultError) as e:
            print(e)
            exit()

    def compute_statistics(self):
        for dataset in self.datasets:
            complete_results = [self.results.get((algorithm, dataset)) for algorithm in self.algorithms]
            num_missing_results = sum(1 for result in complete_results if result in ('XX', None, ''))
            num_failures = sum(1 for result in complete_results if result == '404')
            dataset.nfail = num_missing_results + num_failures
            complete_results = [float(result) for result in complete_results if result and result != '404']
            dataset.average = round(sum(complete_results) / len(complete_results), 1) if complete_results else '-'
            dataset.range = f"{round(min(complete_results), 1)} - {round(max(complete_results), 1)}" if complete_results else '-'

    def find_most_difficult_datasets(self):
        simple_datasets = [dataset for dataset in self.datasets if dataset.type == 'S']
        advanced_datasets = [dataset for dataset in self.datasets if dataset.type == 'A']
        simple_datasets.sort(key=lambda x: x.average, reverse=True)
        advanced_datasets.sort(key=lambda x: x.average, reverse=True)
        return simple_datasets, advanced_datasets

    def find_most_failed_datasets(self):
        simple_datasets = [dataset for dataset in self.datasets if dataset.type == 'S']
        advanced_datasets = [dataset for dataset in self.datasets if dataset.type == 'A']
        simple_datasets.sort(key=lambda x: x.nfail, reverse=True)
        advanced_datasets.sort(key=lambda x: x.nfail, reverse=True)
        return simple_datasets, advanced_datasets

    def compute_scores(self):
        for algorithm in self.algorithms:
            scores = [float(self.results.get((algorithm, dataset))) if self.results.get((algorithm, dataset)) not in ('XX', '404', None, '', '--') else 0 for dataset in self.datasets]
            scores.sort(reverse=True)
            algorithm.score = scores.count(scores[0]) * 3 + scores.count(scores[1]) * 2 + scores.count(scores[2])

    def display_results(self):
        simple_datasets, advanced_datasets = self.find_most_difficult_datasets()
        ml_algorithms, dl_algorithms = self.find_most_failed_datasets()

        with open("reports.txt", "a") as report_file:
            report_file.write(f"Report generated on: {self.report_time}\n\n")
            report_file.write("Simple Dataset Information\n")
            report_file.write("| DatasetID Name Type Weight Ndata Source Average Range Nfail |\n")
            for dataset in simple_datasets:
                dataset_line = f"| {dataset.dataset_id} {dataset.name} {dataset.type} {dataset.weight} {dataset.size} {dataset.source} {dataset.average} {dataset.range} {dataset.nfail} |\n"
                report_file.write(dataset_line)

            report_file.write("\nAdvanced Dataset Information\n")
            report_file.write("| DatasetID Name Type Weight Ndata Source Average Range Nfail |\n")
            for dataset in advanced_datasets:
                dataset_line = f"| {dataset.dataset_id} {dataset.name} {dataset.type} {dataset.weight} {dataset.size} {dataset.source} {dataset.average} {dataset.range} {dataset.nfail} |\n"
                report_file.write(dataset_line)
            
            ml_algorithms = [algorithm for algorithm in self.algorithms if algorithm.category == 'ML']
        dl_algorithms = [algorithm for algorithm in self.algorithms if algorithm.category == 'DL']

        with open("reports.txt", "a") as report_file:
            # ... (other code)

            report_file.write("\nML Algorithm Information\n")
            report_file.write("| Name         Category Year Authors  |\n")
            for algorithm in ml_algorithms:
                authors_str = '-'.join(algorithm.authors)
                algorithm_line = f"| {algorithm.name:<12} {algorithm.category:<4} {algorithm.year:<4} {authors_str:<20} |\n"
                report_file.write(algorithm_line)

            report_file.write("\nDL Algorithm Information\n")
            report_file.write("| Name         Category Year Authors|\n")
            for algorithm in dl_algorithms:
                authors_str = '-'.join(algorithm.authors)
                algorithm_line = f"| {algorithm.name:<12} {algorithm.category:<4} {algorithm.year:<4} {authors_str:<20} |\n"
                report_file.write(algorithm_line)



if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python my_record.py <result_file_name> <dataset_file_name> <algorithm_file_name>")
    else:
        result_file_name = sys.argv[1]
        dataset_file_name = sys.argv[2]
        algorithm_file_name = sys.argv[3]

        records = Records()
        records.read_datasets(dataset_file_name)
        records.read_algorithms(algorithm_file_name)
        records.read_results(result_file_name)

        # Compute statistics, scores, and generate the report
        records.compute_statistics()
        records.compute_scores()
        records.display_results()

        print("Report generated successfully.")
