from textblob import TextBlob
import csv


def sentiment_analysis():
    with open('data/pr_comments.csv', newline='') as in_csv, \
         open('data/comment_sentiment.csv', 'w', newline='') as out_csv:
        reader = csv.reader(in_csv)
        next(reader)
        writer = csv.writer(out_csv)
        writer.writerow(
            ["comment_path", "created", "author", "comment",
             "polarity", "subjectivity"]
        )
        for row in reader:
            blob = TextBlob(row[-1])
            row.extend([blob.sentiment.polarity, blob.sentiment.subjectivity])
            writer.writerow(row)

def main():
    sentiment_analysis()


if __name__ == "__main__":
    main()