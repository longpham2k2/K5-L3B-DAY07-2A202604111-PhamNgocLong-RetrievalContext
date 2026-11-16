# Review sheet

Fill the labels in `reviews.json` (copy of `reviews_template.json`). Read each cited passage: a valid id is not proof of support.

- `answer_grade`: 0 wrong/unsupported, 1 partly correct, 2 correct and complete (abstain = 0)
- `citation_support`: one true/false per citation, in order
- `context_grade`: 0 no evidence in context, 1 evidence but missing condition/source, 2 complete
- `abstention_correct`: true only if it abstained and added no unsupported claims

## t01 (answerable) — answered

**Question:** Why can machine learning models trained on historical data make unfair decisions?

- search `machine learning models historical data unfair decisions bias` → p026:c02 (0.4438), p026:c01 (0.4074), p023:c03 (0.3762)

**Answer:** Machine learning models can make unfair or biased decisions when trained on historical data because the past data itself inherits biases, which the algorithms then replicate [openstax-pds-ch1:B:p026:c02].

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

- search `JSON colon fields` → p033:c02 (0.4199), p034:c00 (0.389), p031:c01 (0.3418)

**Answer:** In JSON, the two fields on either side of a colon are called a key and a value, respectively (key : value).

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

- search `Jupyter Notebook several lines output print` → p043:c00 (0.7377), p042:c01 (0.6656), p042:c00 (0.5872)

**Answer:** If several lines in one cell produce values without print(), only the output from the last line will be shown.

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

- search `Pandas keep rows that meet a condition filtering boolean indexing` → p054:c00 (0.5302), p055:c00 (0.502), p056:c00 (0.439)
- search `DataFrame.loc[] filter rows condition` → p055:c00 (0.6292), p054:c00 (0.5459), p056:c00 (0.5225)

**Answer:** To keep only the rows that meet a specific condition, you can use Pandas' DataFrame.loc[] feature by placing the filtering criteria inside the brackets.

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

> **[openstax-pds-ch1:B:p055:c00]** p55: EXAMPLE 1.13
Problem
Using DataFrame.loc[], search for all the items of Iris-virginica species in the IRIS dataset.
Solution
The following code returns a filtered DataFrame whose species are Iris-virginica. All such rows show up as
an output.
data = pd.read_csv("[Path to ch1-iris.csv]")
data.loc[data['species'] == 'Iris-virginica']
The resulting figure will look like this:

**Expected:** DataFrame.loc[], with the filtering criteria inside the brackets.
**Gold evidence (p54):** To search for some data entries that fulfill specific criteria (i.e., filter), you can use DataFrame.loc[] of
Pandas.
**Gold in final context:** ['openstax-pds-ch1:B:p054:c00']

---

## t05 (answerable) — answered

**Question:** Which tools are known for sophisticated, interactive visualizations of high-dimensional data?

**Filter:** `{'section': '1.4'}`

- search `sophisticated interactive visualizations high-dimensional data tools` → p040:c01 (0.694), p040:c00 (0.6834), p038:c02 (0.4207)

**Answer:** Tableau and PowerBI are user-friendly applications known for offering sophisticated, interactive visualizations for high-dimensional data [openstax-pds-ch1:B:p040:c00].

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

- search `Tableau PowerBI license cost per user per month` → p045:c02 (0.1979), p038:c03 (0.1901), p046:c00 (0.188)
- search `Tableau PowerBI license cost` → p046:c00 (0.211), p033:c00 (0.1941), p041:c02 (0.1878)
- search `Tableau` → p040:c00 (0.3199), p038:c03 (0.2628), p041:c02 (0.2503)

**Answer:** Không đủ bằng chứng trong tài liệu để trả lời.
**Abstain reason:** The chapter does not contain information about the cost of Tableau or PowerBI licenses.

**Absence reason:** Page 40 describes Tableau and PowerBI as user-friendly visualization and dashboard tools but gives no price, subscription or licensing information.

---

## tn02 (no evidence) — abstain

**Question:** What is the Pearson correlation coefficient between US gross and worldwide gross in the movie profit dataset?

- search `Pearson correlation coefficient US gross worldwide gross movie profit dataset` → p057:c01 (0.4482), p058:c00 (0.4386), p047:c00 (0.3502)
- search `correlation coefficient movie profit dataset US_Gross Worldwide_Gross` → p057:c01 (0.4846), p058:c00 (0.4697), p047:c00 (0.3996)
- search `Pearson correlation coefficient` → p057:c01 (0.302), p058:c00 (0.2744), p049:c01 (0.1857)

**Answer:** Không đủ bằng chứng trong tài liệu để trả lời.
**Abstain reason:** The chapter mentions the US gross and worldwide gross of the movie profit dataset in a scatterplot example, but it does not state their Pearson correlation coefficient.

**Absence reason:** Pages 57-58 draw a scatterplot of US_Gross_Million vs Worldwide_Gross_Million and state only that it shows a positive correlation; no coefficient value is computed or reported, and correlation analysis is deferred to a later chapter. Correct behavior: say the value is not given (mentioning that the plot shows a positive correlation is acceptable); any numeric coefficient fails.

---
