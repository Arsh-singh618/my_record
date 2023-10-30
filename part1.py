class Dataset:
    def __init__(self, dataset_id, name, version, size, source):
        self.dataset_id = dataset_id
        self.name = name
        self.version = version
        self.size = size
        self.source = source

class Algorithm:
    def __init__(self, name, category, year, developers):
        self.name = name
        self.category = category
        self.year = year
        self.developers = developers

class Records:
    def __init__(self):
        self.datasets = []
        self.algorithms = []
        self.results = {}

    def add_dataset(self, dataset):
        self.datasets.append(dataset)

    def add_algorithm(self, algorithm):
        self.algorithms.append(algorithm)

    def read_datasets(self, dataset_file_name):
        with open(dataset_file_name, 'r') as file:
            for line in file:
                data = line.strip().split(', ')
                dataset_id, name, version, size, source = data
                dataset = Dataset(dataset_id, name, version, size, source)
                self.add_dataset(dataset)

    def read_algorithms(self, algorithm_file_name):
        with open(algorithm_file_name, 'r') as file:
            for line in file:
                data = line.strip().split(', ')
                name, category, year, *developers = data
                algorithm = Algorithm(name, category, year, developers)
                self.add_algorithm(algorithm)

    def read_results(self, result_file_name):
        with open(result_file_name, 'r') as file:
            for line in file:
                data = line.strip().split(', ')
                algorithm_name = data[0]
                results = data[1:]
                algorithm = next((alg for alg in self.algorithms if alg.name == algorithm_name), None)
                if algorithm:
                    for i, result in enumerate(results):
                        dataset_id, result_value = result.split(': ')
                        if dataset_id == '404':
                            result_value = '--'
                        dataset = next((ds for ds in self.datasets if ds.dataset_id == dataset_id), None)
                        if dataset:
                            self.results[(algorithm, dataset)] = result_value

    def display_results(self):
        print("RESULTS")
        header = "| Algorithms"
        for dataset in self.datasets:
            header += f" {dataset.dataset_id}"
        header += " |"
        print(header)
        for algorithm in self.algorithms:
            result_line = f"| {algorithm.name}"
            for dataset in self.datasets:
                result = self.results.get((algorithm, dataset))
                if result is None or result == '':
                    result_line += " XX"
                elif result == '404':
                    result_line += " --"
                else:
                    result_line += f" {result}"
            result_line += " |"
            print(result_line)

        total_algorithms = len(self.algorithms)
        total_datasets = len(self.datasets)
        nonexistent_results = sum(1 for result in self.results.values() if result == 'XX' or result is None or result == '')
        ongoing_results = sum(1 for result in self.results.values() if result == '--' or result == '404')

        print("\nRESULTS SUMMARY")
        print(f"There are {total_algorithms} algorithms and {total_datasets} datasets.")
        print(f"The number of nonexistent results is {nonexistent_results} and ongoing results is {ongoing_results}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python my_record.py <algorithm_file_name> <result_file_name> <dataset_file_name>")
    else:
        algorithm_file_name = sys.argv[1]
        result_file_name = sys.argv[2]
        dataset_file_name = sys.argv[3]

        records = Records()
        records.read_datasets(dataset_file_name)
        records.read_algorithms(algorithm_file_name)
        records.read_results(result_file_name)
        records.display_results()