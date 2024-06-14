import re
from collections import Counter, defaultdict
from urllib.parse import urlparse
import matplotlib.pyplot as plt


class DomainCounts:
    def extract_domain(self, url):
        parsed_url = urlparse(url)
        return parsed_url.netloc

    def strip_www(self, url):
        return re.sub(r'^www\.', '', url)

    def main(self, input_file):
        domain_counts = {}
        unique_urls = defaultdict(set)

        try:
            with open(input_file, "r") as txtfile:
                for line in txtfile:
                    url = line.strip()  # Remove leading/trailing whitespace
                    domain = self.extract_domain(url)
                    domain = self.strip_www(domain)
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1
                    unique_urls[domain].add(url)

            # Convert unique URL sets to counts
            unique_counts = {domain: len(urls) for domain, urls in unique_urls.items()}

            # Sort domains by count (most common first)
            sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)

            # Print the sorted list
            totalcount = 0
            for domain, count in sorted_domains:
                unique_count = unique_counts[domain]
                print(f"{domain}: {count} (Unique: {unique_count})")
                totalcount = totalcount + unique_count
            print(totalcount)

            # Call the function to plot
            self.plot_domain_counts(domain_counts, unique_counts, top_n=10)

        except FileNotFoundError:
            print(f"File '{input_file}' not found.")

    # Function to plot domain counts
    def plot_domain_counts(self, domain_counts, unique_counts, top_n=10):
        # Get the top N domains by total count
        top_domains = Counter(domain_counts).most_common(top_n)

        # Separate the domains and counts for plotting
        domains, counts = zip(*top_domains)
        unique_counts_sorted = [unique_counts[domain] for domain in domains]

        # Plotting
        bar_width = 0.4
        fig, ax = plt.subplots(figsize=(10, 6))

        # Position of bars on the x-axis
        r1 = range(len(domains))
        r2 = [x + bar_width for x in r1]

        # Create bars
        ax.barh(r1, counts, color='skyblue', height=bar_width, edgecolor='grey', label='Total URLs')
        ax.barh(r2, unique_counts_sorted, color='lightgreen', height=bar_width, edgecolor='grey', label='Unique URLs')

        # Labels and title
        ax.set_xlabel('Count')
        ax.set_ylabel('Domain')
        ax.set_title(f'Top {top_n} Most Frequent Domains')
        ax.set_yticks([r + bar_width / 2 for r in range(len(domains))])
        ax.set_yticklabels(domains)
        ax.invert_yaxis()  # Invert y-axis to show the highest count on top
        ax.legend()

        plt.show()


if __name__ == "__main__":
    dc = DomainCounts()
    dc.main("/Users/delveccj/PycharmProjects/RussiaVsUkraineKnowledgeStore/scripts/files/urls.txt")
