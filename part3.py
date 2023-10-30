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

    def compute_statistics(self, results, datasets):
        complete_results = [results.get((self, dataset)) for dataset in datasets if results.get((self, dataset)) not in ('XX', None, '', '--')]
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
        return f"| {name:<12} {self.category:<4} {self.year:<4} {authors_str:<20} {self.average:^7.1f} {self.nfail:^5} {fail_dataset_str:<12} {self.ongoing_results:^7} |"


    
    
    
    
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
                name, category, year, *authors = data
                algorithm = Algorithm(name, category, int(year), authors)
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

    def display_algorithm_information(self):
        print("\nALGORITHM INFORMATION")
        header = "| Name Туре Year Authors Average Nfail FailDataset Nongoing |"
        print(header)
        for algorithm in self.algorithms:
            algorithm.compute_statistics(self.results, self.datasets)
            print(algorithm)

        best_algorithms = [alg for alg in self.algorithms if alg.average == max(alg.average for alg in self.algorithms)]
        least_failure_algorithms = [alg for alg in self.algorithms if alg.nfail == min(alg.nfail for alg in self.algorithms)]

        best_algorithm_names = ', '.join(alg.name for alg in best_algorithms)
        least_failure_algorithm_names = ', '.join(alg.name for alg in least_failure_algorithms)

        print("\nALGORITHM SUMMARY")
        print(f"The best algorithm{'s' if len(best_algorithms) > 1 else ''} is {best_algorithm_names} with an average result of {best_algorithms[0].average}.")
        print(f"The algorithm{'s' if len(least_failure_algorithms) > 1 else ''} with the least failure{'s' if len(least_failure_algorithms) > 1 else ''} is {least_failure_algorithm_names} with the number of failures being {least_failure_algorithms[0].nfail}.")


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

        # Display the algorithm information in the desired format
        records.display_algorithm_information()