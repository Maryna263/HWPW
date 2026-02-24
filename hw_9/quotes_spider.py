import scrapy
import json

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ["http://quotes.toscrape.com"]
    
    quotes_data = []
    authors_data = {}

    def parse(self, response):
        for quote in response.css("div.quote"):
            # Збір цитат
            tags = quote.css("div.tags a.tag::text").getall()
            author_name = quote.css("small.author::text").get()
            text = quote.css("span.text::text").get()
            
            self.quotes_data.append({
                "tags": tags,
                "author": author_name,
                "quote": text
            })

            # Перехід на сторінку автора, якщо ми його ще не обробили
            author_url = quote.css("span a::attr(href)").get()
            yield response.follow(author_url, self.parse_author)

        # Пагінація
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_author(self, response):
        name = response.css("h3.author-title::text").get().strip()
        if name not in self.authors_data:
            self.authors_data[name] = {
                "fullname": name,
                "born_date": response.css("span.author-born-date::text").get(),
                "born_location": response.css("span.author-born-location::text").get(),
                "description": response.css("div.author-description::text").get().strip()
            }

    def closed(self, reason):
        # Збереження у JSON файли при завершенні
        with open("quotes.json", "w", encoding="utf-8") as f:
            json.dump(self.quotes_data, f, ensure_ascii=False, indent=4)
        
        with open("authors.json", "w", encoding="utf-8") as f:
            json.dump(list(self.authors_data.values()), f, ensure_ascii=False, indent=4)