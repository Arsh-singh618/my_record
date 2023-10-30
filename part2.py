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
                dataset_id, name, weight, size, source = data
                dataset = Dataset(dataset_id, name, int(weight), int(size), source)
                self.add_dataset(dataset)

    def read_algorithms(self, algorithm_file_name):
        with open(algorithm_file_name, 'r') as file:
            for line in file:
                data = line.strip().split(', ')
                name, category, year, *developers = data
                algorithm = Algorithm(name, category, int(year), developers)
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

    def compute_statistics(self):
        for dataset in self.datasets:
            complete_results = [self.results.get((algorithm, dataset)) for algorithm in self.algorithms]
            num_missing_results = sum(1 for result in complete_results if result in ('XX', None, ''))
            num_failures = sum(1 for result in complete_results if result == '404')
            dataset.nfail = num_missing_results + num_failures
            complete_results = [float(result) for result in complete_results if result and result != '404']
            dataset.average = round(sum(complete_results) / len(complete_results), 1) if complete_results else '-'
            dataset.range = f"{round(min(complete_results), 1)} - {round(max(complete_results), 1)}" if complete_results else '-'

    def find_most_difficult_dataset(self):
        difficult_datasets = [dataset for dataset in self.datasets if dataset.average == min(ds.average for ds in self.datasets)]
        return difficult_datasets

    def find_most_failed_dataset(self):
        failed_datasets = [dataset for dataset in self.datasets if dataset.nfail == max(ds.nfail for ds in self.datasets)]
        return failed_datasets

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

    def display_dataset_information(self):
        self.compute_statistics()
        print("\nDATASET INFORMATION")
        header = "| DatasetID Name Type Weight Ndata Source Average Range Nfail |"
        print(header)
        for dataset in self.datasets:
            dataset_line = f"| {dataset.dataset_id} {dataset.name} {dataset.type} {dataset.weight} {dataset.size} {dataset.source} {dataset.average} {dataset.range} {dataset.nfail} |"
            print(dataset_line)

        most_difficult_datasets = self.find_most_difficult_dataset()
        most_failed_datasets = self.find_most_failed_dataset()

        print("\nDATASET SUMMARY")
        if len(most_difficult_datasets) == 1:
            print(f"The most difficult dataset is {most_difficult_datasets[0].name} with an average result of {most_difficult_datasets[0].average}.")
        else:
            print("The most difficult dataset is:")
            for dataset in most_difficult_datasets:
                print(f"- {dataset.name} with an average result of {dataset.average}.")

        if len(most_failed_datasets) == 1:
            print(f"The dataset with the most failures is {most_failed_datasets[0].name} with the number of failures being {most_failed_datasets[0].nfail}.")
        else:
            print("The dataset with the most failures is:")
            for dataset in most_failed_datasets:
                print(f"- {dataset.name} with the number of failures being {dataset.nfail}.")


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
        records.display_dataset_information()
