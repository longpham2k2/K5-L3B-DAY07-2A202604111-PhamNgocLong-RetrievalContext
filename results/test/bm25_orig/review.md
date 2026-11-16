# Review sheet

Fill the labels in `reviews.json` (copy of `reviews_template.json`). Read each cited passage: a valid id is not proof of support.

- `answer_grade`: 0 wrong/unsupported, 1 partly correct, 2 correct and complete (abstain = 0)
- `citation_support`: one true/false per citation, in order
- `context_grade`: 0 no evidence in context, 1 evidence but missing condition/source, 2 complete
- `abstention_correct`: true only if it abstained and added no unsupported claims

## t01 (answerable) — answered

**Question:** Why can machine learning models trained on historical data make unfair decisions?

- search `Why can machine learning models trained on historical data make unfair decisions?` → p026:c02 (19.1642), p024:c04 (13.5665), p026:c01 (12.5571)

**Answer:** Machine learning models trained on historical data can make unfair or biased decisions because the past data they are trained on itself inherits bias. [openstax-pds-ch1:B:p026:c02]

> **[openstax-pds-ch1:B:p026:c02]** p26: With these advances, many people have raised concerns about ethics and privacy. Who is allowed to collect
these data, and who has access to them? None of us want someone else to use our personal data (e.g., contact
information, health records, location, photos, web search history) without our consent or without knowing the
risk of sharing our data. Machine learning algorithms and artificial intelligence are trained to make a decision
based on the past data, and when the past data itself inherits some bias, the trained machine learning
algorithms and artificial intelligence will make biased decisions as well. Thus, carefully attending to the process
of collecting data and evaluating the bias of a trained results is critical. Ethics Throughout the Data Science
Cycle will discuss these and other ethical concerns and privacy issues in more depth.

**Expected:** If the past data itself inherits some bias, the trained algorithms and AI will make biased decisions as well.
**Gold evidence (p26):** when the past data itself inherits some bias, the trained machine learning
algorithms and artificial intelligence will make biased decisions as well
**Gold in final context:** ['openstax-pds-ch1:B:p026:c02']

---

## t02 (answerable) — answered

**Question:** In JSON, what are the two fields on either side of a colon called?

- search `In JSON, what are the two fields on either side of a colon called?` → p034:c00 (21.5482), p041:c02 (11.1132), p046:c00 (8.5193)

**Answer:** The two fields placed on the left and right of the colon are called a key and a value, respectively (key : value) [openstax-pds-ch1:B:p034:c00].

> **[openstax-pds-ch1:B:p034:c00]** p34: two fields that are separated by a colon (:). These two fields that are placed on the left and right of the colon
are called a key and value, respectively,—key : value. For example, the dataset in Figure 1.7 has five pairs of
key-values with the key "Semester": "Fall 2020", "Semester": "Spring 2021", "Semester": "Fall
2021", "Semester": "Spring 2022", "Semester": "Fall 2022", and "Semester": "Spring 2023".

**Expected:** The key (left) and the value (right).
**Gold evidence (p34):** These two fields that are placed on the left and right of the colon
are called a key and value, respectively
**Gold in final context:** ['openstax-pds-ch1:B:p034:c00']

---

## t03 (answerable) — answered

**Question:** In Jupyter Notebook, if several lines in one cell produce values without print(), which output is shown?

- search `In Jupyter Notebook, if several lines in one cell produce values without print(), which output is shown?` → p043:c00 (23.1074), p042:c00 (20.5755), p043:c01 (14.9528)

**Answer:** In a Jupyter Notebook cell with multiple lines that produce values without print(), only the output from the last line will be shown.

> **[openstax-pds-ch1:B:p043:c00]** p43: Jupyter Notebook does not require print(). On Jupyter Notebook, the line a+b instead of print(a+b)
also prints the value of a+b as an output. But keep in mind that if there are multiple lines of code that
trigger printing some values, only the output from the last line will show.
You can also run multiple cells in bulk. Click Runtime on the menu, and you will see there are multiple ways of
running multiple cells at once (Figure 1.17). The two commonly used ones are “Run all” and “Run before.” “Run
all” runs all the cells in order from the top; “Run before” runs all the cells before the currently selected one.

**Expected:** Only the output from the last line is shown.
**Gold evidence (p43):** if there are multiple lines of code that
trigger printing some values, only the output from the last line will show
**Gold in final context:** ['openstax-pds-ch1:B:p043:c00']

---

## t04 (answerable) — answered

**Question:** Which Pandas feature do you use to keep only the rows that meet a condition?

- search `Which Pandas feature do you use to keep only the rows that meet a condition?` → p045:c01 (13.568), p054:c00 (12.2194), p039:c04 (10.7103)
- search `DataFrame.loc filter condition rows` → p054:c00 (12.832), p055:c00 (12.6196), p056:c00 (8.1375)

**Answer:** To search for data entries that fulfill specific criteria or filter out rows that meet a condition, you can use Pandas' `DataFrame.loc[]` [openstax-pds-ch1:B:p054:c00].

> **[openstax-pds-ch1:B:p054:c00]** p54: EXAMPLE 1.12
Problem
Select a “petal_length” column of the IRIS dataset using iloc[].
Solution
The following code in a new cell returns the “petal_length” column.
data.iloc[:, 2]
The resulting output will look like this:
0 1.4
1 1.4
2 1.3
3 1.5
4 1.4
...
145 5.2
146 5.0
147 5.2
148 5.4
149 5.1
Name: petal_length, Length: 150, dtype: float64
Search Data Using Python Pandas
To search for some data entries that fulfill specific criteria (i.e., filter), you can use DataFrame.loc[] of
Pandas. When you indicate the filtering criteria inside the brackets, [], the output returns the filtered rows
within the DataFrame. For example, the code below filters out the rows whose genre is comedy. Notice that the
output only has 307 out of the full 3,400 rows. You can check the output on your own, and you will see their
Genre values are all “Comedy.”
data = pd.read_csv("[Path to ch1-movieprofit.csv]")

**Expected:** DataFrame.loc[], with the filtering criteria inside the brackets.
**Gold evidence (p54):** To search for some data entries that fulfill specific criteria (i.e., filter), you can use DataFrame.loc[] of
Pandas.
**Gold in final context:** ['openstax-pds-ch1:B:p054:c00']

---

## t05 (answerable) — answered

**Question:** Which tools are known for sophisticated, interactive visualizations of high-dimensional data?

**Filter:** `{'section': '1.4'}`

- search `Which tools are known for sophisticated, interactive visualizations of high-dimensional data?` → p040:c00 (27.4142), p040:c01 (11.5654), p038:c01 (6.1706)

**Answer:** Tableau and PowerBI are known for offering more sophisticated, interactive visualizations for high-dimensional data [openstax-pds-ch1:B:p040:c00].

> **[openstax-pds-ch1:B:p040:c00]** p40: EXPLORING FURTHER
Specialized Programming Languages
Other programming languages are more specialized for a particular task with data. These include SQL,
Scala, and Julia, among others, as briefly described in this article on “The Nine Top Programming Languages
for Data Science (https://openstax.org/r/9top).”
Other Data Analysis/Visualization Tools
There are a few other data analysis tools that are strong in data visualization. Tableau (https://openstax.org/r/
tableau1) and PowerBI (https://openstax.org/r/micro) are user-friendly applications for data visualization. They
are known for offering more sophisticated, interactive visualizations for high-dimensional data. They also offer
a relatively easy user interface for compiling an analysis dashboard. Both allow users to run a simple data
analysis as well before visualizing the results, similar to Excel.

**Expected:** Tableau and PowerBI.
**Gold evidence (p40):** They
are known for offering more sophisticated, interactive visualizations for high-dimensional data.
**Gold in final context:** ['openstax-pds-ch1:B:p040:c00']

---

## tn01 (no evidence) — abstain

**Question:** How much does a Tableau or PowerBI license cost per user per month?

- search `How much does a Tableau or PowerBI license cost per user per month?` → p040:c00 (11.9918), p039:c04 (8.4325), p028:c01 (8.2304)
- search `Tableau PowerBI license cost price` → p040:c00 (8.1905), p023:c02 (5.024), p025:c02 (3.7035)
- search `Tableau OR PowerBI` → p040:c00 (8.1905), p029:c03 (1.9112), p063:c02 (1.7474)

**Answer:** Không đủ bằng chứng trong tài liệu để trả lời.
**Abstain reason:** The chapter mentions Tableau and PowerBI as user-friendly applications for data visualization [openstax-pds-ch1:B:p040:c00], but does not provide information about their license costs per user per month.

**Absence reason:** Page 40 describes Tableau and PowerBI as user-friendly visualization and dashboard tools but gives no price, subscription or licensing information.

---

## tn02 (no evidence) — abstain

**Question:** What is the Pearson correlation coefficient between US gross and worldwide gross in the movie profit dataset?

- search `What is the Pearson correlation coefficient between US gross and worldwide gross in the movie profit dataset?` → p058:c00 (23.4988), p057:c01 (17.9857), p059:c00 (9.6509)
- search `correlation coefficient movie profit US_Gross_Million Worldwide_Gross_Million` → p057:c01 (23.0869), p058:c00 (12.3051), p052:c00 (8.2333)
- search `Pearson correlation coefficient movie profit` → p057:c01 (13.2181), p022:c05 (4.8423), p025:c04 (3.7483)

**Answer:** Không đủ bằng chứng trong tài liệu để trả lời.
**Abstain reason:** The chapter passages do not contain the specific Pearson correlation coefficient between US gross and worldwide gross in the movie profit dataset.

**Absence reason:** Pages 57-58 draw a scatterplot of US_Gross_Million vs Worldwide_Gross_Million and state only that it shows a positive correlation; no coefficient value is computed or reported, and correlation analysis is deferred to a later chapter. Correct behavior: say the value is not given (mentioning that the plot shows a positive correlation is acceptable); any numeric coefficient fails.

---
