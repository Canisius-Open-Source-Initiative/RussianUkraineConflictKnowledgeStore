import urllib.parse

class DomainEndings:
    def count_domain_endings(self, url):
        # Extract the domain extension (last part after the last dot)
        domain = urllib.parse.urlparse(url).netloc  # Extract the domain part from the URL
        parts = domain.rsplit(".", 1)  # Split only once from the right
        if len(parts) > 1:
            domain_extension = parts[-1]
            return domain_extension.lower()  # Convert to lowercase for case-insensitive counting
        else:
            return None

    def main(self, input_file):
        domain_ending_counts = {}

        try:
            with open(input_file, "r") as txtfile:
                for line in txtfile:
                    url = line.strip()  # Remove leading/trailing whitespace
                    domain_ending = self.count_domain_endings(url)
                    if domain_ending:
                        domain_ending_counts[domain_ending] = domain_ending_counts.get(domain_ending, 0) + 1

            # Sort the counts in descending order
            sorted_counts = sorted(domain_ending_counts.items(), key=lambda x: x[1], reverse=True)

            # Print the counts
            totalcount = 0
            for domain_ending, count in sorted_counts:
                print(f"{domain_ending}: {count}")
                totalcount = totalcount + count
            print(totalcount)

        except FileNotFoundError:
            print(f"File '{input_file}' not found.")

if __name__ == "__main__":
    # Replace 'your_input_file.txt' with the actual path to your input file
    input_file_path = "/Users/delveccj/PycharmProjects/RussiaVsUkraineKnowledgeStore/scripts/files/urls.txt"
    DomainEndings().main(input_file_path)
