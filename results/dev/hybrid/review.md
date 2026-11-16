# Review sheet

Fill the labels in `reviews.json` (copy of `reviews_template.json`). Read each cited passage: a valid id is not proof of support.

- `answer_grade`: 0 wrong/unsupported, 1 partly correct, 2 correct and complete (abstain = 0)
- `citation_support`: one true/false per citation, in order
- `context_grade`: 0 no evidence in context, 1 evidence but missing condition/source, 2 complete
- `abstention_correct`: true only if it abstained and added no unsupported claims

## d01 (answerable) — answered

**Question:** According to the Anaconda (2020) survey, how much of the data science process do data scientists spend on data collection and cleaning?

- search `Anaconda 2020 survey data collection and cleaning` → p021:c01 (0.032258), p021:c00 (0.032018), p063:c01 (0.030769)

**Answer:** According to the Anaconda (2020) survey, data scientists spend about half of the entire process on data collection and cleaning [openstax-pds-ch1:B:p021:c00].

> **[openstax-pds-ch1:B:p021:c00]** p21: Figure 1.3 The Data Science Cycle
Although data collection and preparation may sound like simple tasks compared to the more important work
of analysis, they are actually the most time- and effort-consuming steps in the data science cycle. According to
a survey conducted by Anaconda (2020), data scientists spend about half of the entire process in data
collection and cleaning, while data analysis and communication take about a quarter to a third of the time
each, depending on the job.

**Expected:** About half of the entire process.
**Gold evidence (p21):** data scientists spend about half of the entire process in data
collection and cleaning
**Gold in final context:** ['openstax-pds-ch1:B:p021:c00']

---

## d02 (answerable) — answered

**Question:** What stages does a data science project go through, in order?

- search `stages data science project order` → p019:c02 (0.031258), p021:c01 (0.031054), p062:c01 (0.03101)
- search `data science cycle steps order` → p021:c00 (0.032522), p020:c04 (0.032266), p019:c02 (0.031514)

**Answer:** The data science cycle goes through the following stages in order: problem definition, data collection, preparation, analysis, and reporting [openstax-pds-ch1:B:p020:c04].

> **[openstax-pds-ch1:B:p020:c04]** p20: The Data Science Cycle
Data science tasks follow a process, called the data science cycle, which includes problem definition, then
data collection, preparation, analysis, and reporting, as illustrated in Figure 1.3. See this animation about data
science (https://openstax.org/r/youtube), which describes the data science cycle in much the same way.

**Expected:** Problem definition, data collection, data preparation, data analysis, and data reporting (the data science cycle).
**Gold evidence (p20):** called the data science cycle, which includes problem definition, then
data collection, preparation, analysis, and reporting
**Gold in final context:** ['openstax-pds-ch1:B:p020:c04']

---

## d03 (answerable) — answered

**Question:** What did Walmart learn about strawberry Pop-Tart sales before Hurricane Frances?

- search `Walmart strawberry Pop-Tart Hurricane Frances` → p023:c01 (0.032787), p023:c00 (0.032258), p023:c02 (0.029911)

**Answer:** Walmart discovered that strawberry Pop-Tart sales increased by about sevenfold during a previous hurricane, prompting them to ship extra supplies ahead of Hurricane Frances.

> **[openstax-pds-ch1:B:p023:c01]** p23: A week before the hurricane’s arrival, staff were asked to look back at their data
on sales during Hurricane Charley, which hit several weeks earlier, and then come up with some forecasts
about product demand ahead of Frances (Hays, 2004). Among other insights, the executives discovered that
strawberry Pop-Tart sales increased by about sevenfold during that time. As a result, in the days before
Hurricane Frances, Walmart shipped extra supplies of strawberry Pop-Tarts to stores in the storm’s path (Hays,
2004). The analysis also provided insights on how many checkout associates to assign at different times of the
day, where to place popular products, and many other sales and product details. In addition, the company has
launched social media analytics efforts to investigate hot keywords on social media and promptly make related
products available (ProjectPro, 2015).

**Expected:** Strawberry Pop-Tart sales increased about sevenfold during the earlier hurricane, so Walmart shipped extra supplies to stores in the storm's path.
**Gold evidence (p23):** strawberry Pop-Tart sales increased by about sevenfold during that time
**Gold in final context:** ['openstax-pds-ch1:B:p023:c01']

---

## d04 (answerable) — answered

**Question:** How did Amazon reorganize its warehousing to cut delivery time and cost?

- search `Amazon reorganize warehousing cut delivery time and cost` → p023:c02 (0.032787), p023:c03 (0.032258), p022:c02 (0.031498)

**Answer:** Amazon divided the United States into eight geographic regions to ensure that most items were warehoused and shipped within the same region, and it uses machine learning algorithms to predict regional demand and stock high-demand items in advance at the corresponding fulfillment centers [openstax-pds-ch1:B:p023:c02].

> **[openstax-pds-ch1:B:p023:c02]** p23: Amazon provides another good example. Ever since it launched its Prime membership service, Amazon has
focused on how to minimize delivery time and cost. Like Walmart, it started by analyzing consumer patterns
and was able to place products close to customers. To do so, Amazon first divided the United States into eight
geographic regions and ensured that most items were warehoused and shipped within the same region; this
allowed the company to reduce the shipping time and cost. As of 2023, more than 76% of orders were shipped
from within the customer’s region, and items in same-day shipping facilities could be made ready to put on a
delivery truck in just 11 minutes (Herrington, 2023). Amazon also utilizes machine learning algorithms to
predict the demand for items in each region and have the highest-demand items available in advance at the
fulfillment center of the corresponding region.

**Expected:** It divided the United States into eight geographic regions and warehoused and shipped most items within the same region.
**Gold evidence (p23):** Amazon first divided the United States into eight
geographic regions and ensured that most items were warehoused and shipped within the same region
**Gold in final context:** ['openstax-pds-ch1:B:p023:c02']

---

## d05 (answerable) — answered

**Question:** What do the street sensors installed in San Diego measure, and what do they control?

- search `San Diego street sensors measure control` → p024:c01 (0.032522), p024:c02 (0.032522), p024:c00 (0.031746)

**Answer:** The street sensors installed in San Diego measure traffic, parking occupancy, humidity, and temperature, and they control the streetlights to turn on only when necessary [openstax-pds-ch1:B:p024:c01, openstax-pds-ch1:B:p024:c02].

> **[openstax-pds-ch1:B:p024:c01]** p24: Data Science in Public Policy
Smart cities are among the most representative examples of the use of data science in public policy. Multiple
cities around the world, including Masdar City in the United Arab Emirates and Songdo in South Korea, have
installed thousands of data-collecting sensors used to optimize their energy consumption. The technology is
not perfect, and smart cities may not yet live up to their full potential, but many corporations and companies
are pursuing the goal of developing smart cities more broadly (Clewlow, 2024). The notion of a smart city has
also been applied on a smaller scale, such as to a parking lot, a building, or a street of lights. For example, the
city of San Diego installed thousands of sensors on the city streets to control the streetlights using data and
smart technology.

> **[openstax-pds-ch1:B:p024:c02]** p24: The sensors measure traffic, parking occupancy, humidity, and temperature and are able to
turn on the lights only when necessary (Van Bocxlaer, 2020). New York City has adopted smart garbage bins
that monitor the amount of garbage in a bin, allowing garbage collection companies to route their collection
efforts more efficiently (Van Bocxlaer, 2020).
EXPLORING FURTHER
Sensor Networks to Monitor Energy Consumption
See how Songdo (https://openstax.org/r/youtube4) monitors energy consumption and safety with sensor
networks.

**Expected:** Traffic, parking occupancy, humidity, and temperature; they turn on the streetlights only when necessary.
**Gold evidence (p24):** The sensors measure traffic, parking occupancy, humidity, and temperature and are able to
turn on the lights only when necessary
**Gold in final context:** ['openstax-pds-ch1:B:p024:c02']

---

## d06 (answerable) — answered

**Question:** Which overlooked player statistics did the Oakland Athletics focus on using sabermetrics?

- search `Oakland Athletics sabermetrics player statistics overlooked` → p025:c03 (0.032787), p025:c04 (0.032258), p049:c01 (0.031498)

**Answer:** Using sabermetrics, the Oakland Athletics focused on traditionally overlooked metrics such as on-base percentage and slugging percentage [openstax-pds-ch1:B:p025:c03].

> **[openstax-pds-ch1:B:p025:c03]** p25: Data Science in Sports and Entertainment
Data science is prevalent in the sports and the entertainment industry as well. Sports naturally produce much
data—about the player, positions, teams, seasons, and so on. Therefore, just as there is the concept of
business analytics, the analysis of such data in sports is called sports analytics. For example, the Oakland
Athletics baseball team famously analyzed player recruitment for the 2002 season. The team’s management
adapted a statistical approach referred to as sabermetrics to recruit and position players. With sabermetrics,
the team was able to identify critical yet traditionally overlooked metrics such as on-base percentage and
slugging percentage.

**Expected:** On-base percentage and slugging percentage.
**Gold evidence (p25):** identify critical yet traditionally overlooked metrics such as on-base percentage and
slugging percentage
**Gold in final context:** ['openstax-pds-ch1:B:p025:c03']

---

## d07 (answerable) — answered

**Question:** Under what condition would class size be considered discrete rather than continuous data?

- search `class size discrete continuous data` → p028:c04 (0.032787), p028:c03 (0.032258), p027:c01 (0.030777)

**Answer:** Class size is considered discrete data if the campus enforces a restriction for all classes to be 200 seats or less, making the possible values a finite set of 200 numbers.

> **[openstax-pds-ch1:B:p028:c04]** p28: From the previous example, the class size 100, 150, etc. are numbers with the implied unit “students.” Also,
they indicate measurable quantities as they are head counts. Therefore, the class size is numeric data. It is also
continuous data since the size numbers seem to be any natural numbers and these numbers are chosen from
an infinite set of numbers, the set of natural numbers. Note that whether data is continuous (or discrete) also
depends on the context. For example, the same class size data can be discrete if the campus enforces all
classes to be 200 seats or less. Such restriction makes the class size values be chosen from a finite set of 200
numbers: 1, 2, 3, …, 198, 199, 200.

**Expected:** If the campus caps every class at 200 seats or less, class size is chosen from a finite set (1 to 200) and becomes discrete.
**Gold evidence (p28):** the same class size data can be discrete if the campus enforces all
classes to be 200 seats or less
**Gold in final context:** ['openstax-pds-ch1:B:p028:c04']

---

## d08 (answerable) — answered

**Question:** What is the difference between nominal and ordinal data?

- search `nominal ordinal data difference` → p029:c00 (0.032787), p029:c01 (0.032258), p029:c02 (0.031498)

**Answer:** For nominal data, the set of possible values does not include any ordering notion, whereas for ordinal data, the set of possible values includes an ordering notion (such as a degree or chronological order) [openstax-pds-ch1:B:p029:c00, openstax-pds-ch1:B:p029:c01].

> **[openstax-pds-ch1:B:p029:c00]** p29: Categorical data is represented in different forms such as words, symbols, and even numbers. A categorical
value is chosen from a finite set of values, and the value does not necessarily indicate a measurable quantity.
Categorical data can be divided into nominal data and ordinal data. For nominal data, the set of possible
values does not include any ordering notion, whereas with ordinal data, the set of possible values includes an
ordering notion.

> **[openstax-pds-ch1:B:p029:c01]** p29: The rest—semester, instructor, and ratings—are categorical data. They are represented in symbols (e.g., “Fall
2020,” “A”) or words (e.g., “Highly recommended”), and these values are chosen from the finite set of those
symbols and words (e.g., A vs. B). The former two data are nominal since the semester and instructor do not
have orders to follow, while the latter is ordinal since there is a notion of degree (Not recommended at all ~
Highly recommended). You may argue that the semester could have chronological ordering: Fall 2020 comes
before Spring 2021, Fall 2021 follows Fall 2020. If you want to value that notion for your analysis, you could
consider the semester data to be ordinal as well—the chronological ordering is indeed critical when you are
looking at a time-series dataset. You will learn more about that in Time Series and Forecasting.

**Expected:** Nominal values have no ordering notion; ordinal values include an ordering notion.
**Gold evidence (p29):** For nominal data, the set of possible
values does not include any ordering notion, whereas with ordinal data, the set of possible values includes an
ordering notion.
**Gold in final context:** ['openstax-pds-ch1:B:p029:c00']

---

## d09 (answerable) — answered

**Question:** Why is web data usually stored as JSON or XML rather than CSV?

- search `JSON XML CSV web data stored` → p031:c01 (0.032787), p031:c02 (0.032258), p034:c02 (0.031258)

**Answer:** Web data is stored in JSON or XML rather than CSV because JSON is the most suitable format for exchanging data between a user and a server, and XML's hierarchy-friendly nature makes it best suited for complex datasets, whereas CSV is limited to flat, tabular structures.

> **[openstax-pds-ch1:B:p031:c01]** p31: Datasets can be stored in different formats, and it’s important to be able to recognize the most commonly
used formats. This section covers three of the most often used formats for structured datasets—comma-separated values (CSV), JavaScript Object Notation (JSON), and Extensible Markup Language (XML). While
CSV is the most intuitive way of encoding a tabular dataset, much of the data we would collect from the web
(e.g., websites, mobile applications) is stored in the JSON or XML format. The reason is that JSON is the most
suitable for exchanging data between a user and a server, and XML is the most suitable for complex dataset
due to its hierarchy-friendly nature. Since they all store data as plain texts, you can open them using any
typical text editors such as Notepad, Visual Studio Code, Sublime Text, or VI editor.

> **[openstax-pds-ch1:B:p031:c02]** p31: Table 1.3 summarizes the advantages and disadvantages of CSV, JSON, and XML dataset formats. Each of these
is described in more detail below.
Dataset Format Pros Cons Typical Use
CSV • Simple • Difficult to add
metadata
• Difficult to parse if
there are special
characters
• Flat structure
• Tabular data
JSON • Simple
• Compatible with
many languages
• Easy to parse
• Difficult to add
metadata
• Cannot leave
comments
• Data that needs to
be exchanged
between a user and
a server
XML • Structured (so more
readable)
• Possible to add
metadata
• Verbose
• Complex structure
with tags
• Hierarchical data
structures
Table 1.3 Summary of the CSV, JSON, and XML formats

**Expected:** JSON is most suitable for exchanging data between a user and a server; XML is most suitable for complex datasets because it is hierarchy-friendly.
**Gold evidence (p31):** JSON is the most
suitable for exchanging data between a user and a server, and XML is the most suitable for complex dataset
due to its hierarchy-friendly nature
**Gold in final context:** ['openstax-pds-ch1:B:p031:c01']

---

## d10 (answerable) — answered

**Question:** How many items and attributes does the Jeopardy JSON dataset have?

- search `Jeopardy JSON dataset items attributes` → p038:c00 (0.032787), p037:c01 (0.031754), p034:c01 (0.031281)

**Answer:** The Jeopardy dataset has 409 items, and each item has seven attributes: “category”, “air_date”, “question”, “value”, “answer”, “round”, and “show_number”. [openstax-pds-ch1:B:p038:c00]

> **[openstax-pds-ch1:B:p038:c00]** p38: EXAMPLE 1.8
Problem
The Jeopardy dataset (ch1-jeopardy.json (https://openstax.org/r/filed15)) is formatted in JSON. Download
and open it with a code editor (e.g., Notepad, Sublime Text, Xcode, Visual Studio Code).
• How many items are there in the dataset?
• How many attributes are there in the dataset?
• What is the third item in the dataset?
Solution
There are 409 items in the dataset, and each item has seven attributes: “category”, “air_date”,
“question”, “value”, “answer”, “round”, and “show_number”. The third item is located at index 2 of the first
list as shown in Figure 1.14.
Figure 1.14 The Third Item in the Jeopardy Dataset

**Expected:** 409 items, each with seven attributes.
**Gold evidence (p38):** There are 409 items in the dataset, and each item has seven attributes
**Gold in final context:** ['openstax-pds-ch1:B:p038:c00']

---

## d11 (answerable) — answered

**Question:** After editing several code cells in Colab, how should you run them to avoid errors from execution order?

- search `Colab edit several code cells run execution order errors` → p045:c00 (0.032018), p043:c01 (0.031778), p042:c00 (0.031754)

**Answer:** After making changes across multiple code cells, it is recommended to use "Run all" or "Run before" to ensure your code runs sequentially from the top and avoids execution order errors [openstax-pds-ch1:B:p045:c00].

> **[openstax-pds-ch1:B:p045:c00]** p45: a = 2
a + b
The resulting output will look like this:
5
The value of a has changed to 2. This implies that the execution order of each cell matters! If you have run the
third cell before the second cell, the value of a will have the value from the third one even though the third cell
is located below the second cell. Therefore, it is recommended to use “Run all” or “Run before” after you make
changes across multiple cells of code. This way your code is guaranteed to run sequentially from the top.
Python Pandas
One of the strengths of Python is that it includes a variety of free, open-source libraries. Libraries are a set of
already-implemented methods that a programmer can refer to, allowing a programmer to avoid building
common functions from scratch.

**Expected:** Use "Run all" or "Run before" so the code runs sequentially from the top.
**Gold evidence (p45):** it is recommended to use “Run all” or “Run before” after you make
changes across multiple cells of code
**Gold in final context:** ['openstax-pds-ch1:B:p045:c00']

---

## d12 (answerable) — answered

**Question:** What is the difference between a Pandas DataFrame and a Series?

- search `Pandas DataFrame and Series difference` → p047:c01 (0.032787), p050:c00 (0.032258), p045:c01 (0.03055)

**Answer:** A Pandas DataFrame is used for multi-column tabular data, while a Series is used for single-column data [openstax-pds-ch1:B:p047:c01].

> **[openstax-pds-ch1:B:p047:c01]** p47: DATAFRAME VERSUS SERIES
Pandas defines two data types for tabular data—DataFrame and Series. While DataFrame is used for multi-column tabular data, Series is used for single-column data. Many methods in Pandas support both
DataFrame and Series, but some are only for one or the other. It is always good to check if the method you

**Expected:** A DataFrame stores multi-column tabular data; a Series stores single-column data.
**Gold evidence (p47):** While DataFrame is used for multi-column tabular data, Series is used for single-column data.
**Gold in final context:** ['openstax-pds-ch1:B:p047:c01']

---

## d13 (answerable) — answered

**Question:** How many items are in the Iris Flower dataset, and why does that differ from the number of rows?

**Filter:** `{'section': '1.3'}`

- search `Iris Flower dataset number of items rows` → p037:c01 (0.032522), p037:c02 (0.032522), p037:c00 (0.031498)

**Answer:** There are 150 items in the Iris Flower dataset. This differs from the total of 151 rows because one of those rows is the header row at the top. [openstax-pds-ch1:B:p037:c01]

> **[openstax-pds-ch1:B:p037:c01]** p37: • How many items are there in the dataset?
• How many attributes are there in the dataset?
• What is the second attribute in the dataset?
Solution
There are 151 rows in the dataset with the header row at the top, totaling 150 items. There are five
attributes listed across columns: sepal_length, sepal_width, petal_length, petal_width, species.
The second attribute is sepal_width.

**Expected:** 150 items; the file has 151 rows because the first row is the header.
**Gold evidence (p37):** There are 151 rows in the dataset with the header row at the top, totaling 150 items.
**Gold in final context:** ['openstax-pds-ch1:B:p037:c01']

---

## d14 (answerable) — answered

**Question:** What is the goal of data visualization?

**Filter:** `{'section': '1.1'}`

- search `goal of data visualization` → p022:c00 (0.032787), p022:c01 (0.032002), p021:c01 (0.031754)

**Answer:** The goal of data visualization is to communicate information effectively and facilitate better decision-making.

> **[openstax-pds-ch1:B:p022:c00]** p22: Data Reporting
Data reporting involves the presentation of data in a way that will best convey the information learned from
data analysis. The importance of data reporting cannot be overemphasized. Without it, data scientists cannot
effectively communicate to their audience the insights they discovered in the data. Data scientists work with
domain experts from different fields, and it is their responsibility to communicate the results of their analysis
in a way that those domain experts can understand. Data visualization is a graphical way of presenting and
reporting data to point out the patterns, trends, and hidden insights; it involves the use of visual elements
such as charts, graphs, and maps to present data in a way that is easy to comprehend and analyze. The goal of
data visualization is to communicate information effectively and facilitate better decision-making.

**Expected:** To communicate information effectively and facilitate better decision-making.
**Gold evidence (p22):** The goal of
data visualization is to communicate information effectively and facilitate better decision-making.
**Gold in final context:** ['openstax-pds-ch1:B:p022:c00']

---

## d15 (answerable) — answered

**Question:** Why does the textbook focus on Python instead of other programming languages?

**Filter:** `{'section': '1.4'}`

- search `Python instead of other programming languages` → p039:c02 (0.032522), p039:c01 (0.032002), p040:c00 (0.031778)

**Answer:** The textbook focuses on Python because of its straightforward and intuitive syntax, making it especially easy for beginners to learn and apply, and because Python skills apply to a wide range of computing work [openstax-pds-ch1:B:p039:c02].

> **[openstax-pds-ch1:B:p039:c02]** p39: Python and R are two of the most commonly used programming languages today. Both are open-source
programming languages. While Python started as a general-purpose language that covers various types of
tasks (e.g., numerical computation, data analysis, image processing, and web development), R is more
specifically designed for statistical computing and graphics. Both use simple syntax compared to conventional
programming languages such as Java or C/C++. They offer a broad collection of packages for data
manipulation, statistical analysis, visualization, machine learning, and complex data modeling tasks. We have chosen to focus on Python in this text because of its straightforward and intuitive syntax, which
makes it especially easy for beginners to learn and apply. Also, Python skills can apply to a wide range of
computing work.

**Expected:** Its straightforward and intuitive syntax makes it easy for beginners to learn and apply.
**Gold evidence (p39):** We have chosen to focus on Python in this text because of its straightforward and intuitive syntax
**Gold in final context:** ['openstax-pds-ch1:B:p039:c02']

---

## dn01 (no evidence) — abstain

**Question:** According to the Anaconda (2020) survey, what share of their time do data scientists spend on deploying models to production?

- search `Anaconda 2020 survey share of time deploying models to production` → p021:c00 (0.032522), p021:c01 (0.03055), p023:c02 (0.029514)
- search `Anaconda deploying models to production time` → p021:c00 (0.032787), p023:c02 (0.031054), p023:c05 (0.031054)
- search `Anaconda` → p021:c00 (0.016393), p055:c00 (0.016393), p062:c04 (0.016129)

**Answer:** Không đủ bằng chứng trong tài liệu để trả lời.
**Abstain reason:** The chapter mentions the Anaconda (2020) survey regarding data collection and cleaning time, but does not contain information about the share of time spent on deploying models to production.

**Absence reason:** Page 21 reports the Anaconda (2020) split only for data collection and cleaning (about half) and for data analysis and communication (about a quarter to a third each). Model deployment is not mentioned on any corpus page.

---

## dn02 (no evidence) — abstain

**Question:** What is the median annual salary of data scientists according to the Bureau of Labor Statistics?

- search `median annual salary Bureau of Labor Statistics data scientists` → p032:c00 (0.032787), p063:c01 (0.032002), p020:c00 (0.031281)
- search `salary data scientists` → p019:c01 (0.03101), p020:c01 (0.030415), p021:c00 (0.029958)
- search `salary` → p052:c00 (0.016393), p050:c00 (0.016129), p059:c00 (0.015873)

**Answer:** Không đủ bằng chứng trong tài liệu để trả lời.
**Abstain reason:** The chapter mentions the Bureau of Labor Statistics as a public data source, but does not contain information about the median annual salary of data scientists.

**Absence reason:** The Bureau of Labor Statistics appears only on page 32, in a list of public dataset sources. The chapter gives no salary, wage or job-outlook figures.

---
