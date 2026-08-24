# Power BI Dashboard Guide: Scraped Book Data Visualization

This guide details how to import, clean, transform, and visualize the scraped books data (`books_data.csv`) in **Power BI Desktop**. It contains the complete Power Query (M code) transformations, DAX calculated columns and measures, visual designs, and test verification cases.

---

## 1. Power Query Data Integration & Cleaning (M Code)

To import and clean the books data, follow these steps:
1. Open **Power BI Desktop**.
2. Click on **Get Data** -> **Text/CSV** and select `books_data.csv`.
3. Click on **Transform Data** to open the Power Query Editor.
4. Go to **Advanced Editor** and replace the existing code with the M script below.

### Power Query M Script

```powerquery
let
    // 1. Load the CSV file from local source
    Source = Csv.Document(File.Contents("D:\Internship\books_data.csv"), [Delimiter=",", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    
    // 2. Promote the first row as headers
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    
    // 3. Clean Title (Trim whitespace and handle text type)
    CleanedTitle = Table.TransformColumns(PromotedHeaders, {{"Title", Text.Trim, type text}}),

    // 4. Clean Price column: Remove 'Â£' or '£' characters and trim spaces
    CleanedPriceText = Table.TransformColumns(CleanedTitle, {
        {"Price", each Text.Replace(Text.Replace(Text.Replace(_, "Â", ""), "£", ""), " ", ""), type text}
    }),

    // 5. Convert Price column to Decimal Number (representing Price in GBP)
    RenamedPriceGBP = Table.RenameColumns(CleanedPriceText, {{"Price", "Price_GBP"}}),
    TypedPriceGBP = Table.TransformColumnTypes(RenamedPriceGBP, {{"Price_GBP", type number}}),

    // 6. Convert Rating column to Integer (Whole Number)
    TypedRating = Table.TransformColumnTypes(TypedPriceGBP, {{"Rating", Int64.Type}}),

    // 7. Clean Availability column (Trim whitespace)
    CleanedAvailability = Table.TransformColumns(TypedRating, {{"Availability", Text.Trim, type text}}),

    // 8. Trim URL column
    CleanedURL = Table.TransformColumns(CleanedAvailability, {{"URL", Text.Trim, type text}}),

    // 9. Remove duplicates based on Title and URL to ensure book uniqueness
    RemovedDuplicates = Table.Distinct(CleanedURL, {"Title", "URL"}),

    // 10. Add Custom Column: Convert Price from GBP to USD using the exchange rate 1.32
    AddedPriceUSD = Table.AddColumn(RemovedDuplicates, "Price_USD", each [Price_GBP] * 1.32, type number),
    
    // 11. Final column type formatting
    FinalTypes = Table.TransformColumnTypes(AddedPriceUSD, {
        {"Price_USD", type number}, 
        {"Availability", type text}, 
        {"Title", type text}, 
        {"Rating", Int64.Type}, 
        {"URL", type text}
    })
in
    FinalTypes
```

5. Click **Done** and then click **Close & Apply** to load the clean dataset into Power BI.

---

## 2. Calculated Columns and Measures (DAX)

After applying the data model, create the following calculated column and measures using **DAX**:

### A. Calculated Columns

#### 1. Price Category (USD Conversion)
Categorizes books based on USD pricing thresholds.
- **Budget**: Under $26.40 (Equivalent to £20)
- **Standard**: Between $26.40 and $66.00 (Equivalent to £20–£50)
- **Premium**: Above $66.00 (Equivalent to £50)

```dax
Price Category = 
IF(
    'books_data'[Price_USD] < 26.40, 
    "Budget", 
    IF(
        'books_data'[Price_USD] <= 66.00, 
        "Standard", 
        "Premium"
    )
)
```

---

### B. DAX Measures

Create these measures by right-clicking the `books_data` table and selecting **New Measure**:

#### 1. Average Book Price (USD)
Calculates the average price of books.
```dax
Average Price = AVERAGE('books_data'[Price_USD])
```

#### 2. Total Books
Counts the total number of unique books in the dataset.
```dax
Total Books = COUNTROWS('books_data')
```

#### 3. % In Stock
Calculates the percentage of books that are in stock.
```dax
% In Stock = 
DIVIDE(
    CALCULATE(
        COUNTROWS('books_data'), 
        'books_data'[Availability] = "In stock"
    ),
    COUNTROWS('books_data'),
    0
)
```

---

## 3. Dashboard Design & Layout Configuration

### Theme and Typography
- **Font Family**: Inter or Segoe UI (Clean, modern typeface).
- **Background Color**: Soft gray/white (#F3F4F6) with card tiles in white with light shadows.
- **Color Palette**: Dark charcoal (primary text), Deep Slate Teal (primary visuals), Emerald Green (In stock), Coral/Red (Out of stock/low ratings).

### A. KPI Cards (Top Banner)
Create three **Card** or **Multi-row card** visuals for high-level KPIs:
1. **Total Books**: Bind to the `[Total Books]` measure. Format as Whole Number.
2. **Average Price**: Bind to the `[Average Price]` measure. Format as Currency (`$#,##0.00`).
3. **% In Stock**: Bind to the `[ % In Stock]` measure. Format as Percentage (`0.0%`).

### B. Trend Chart (Average Price by Rating)
- **Visual Type**: Clustered Column Chart.
- **X-Axis**: `Rating` (1 to 5 stars, sorted ascending).
- **Y-Axis**: `[Average Price]` (USD).
- **Format**: Enable Data Labels. Color columns with a gradient (lighter blue for low ratings, deep slate teal for higher ratings).
- **Title**: *Average Book Price by Rating (USD)*

### C. Proportion of Availability
- **Visual Type**: Pie Chart or Donut Chart.
- **Legend**: `Availability` (e.g. "In stock" vs "Out of stock").
- **Values**: `[Total Books]` (or count of Title).
- **Format**: In stock = Green (#10B981), Out of stock = Red (#EF4444).
- **Title**: *Stock Availability Status*

### D. Interactive Slicers (Sidebar)
Add three **Slicer** visuals for filtering:
1. **Rating Slicer**: Vertical list or tile slider using `Rating` (1 to 5).
2. **Stock Availability Slicer**: Vertical list or dropdown using `Availability` ("In stock", "Out of stock").
3. **Price Range Slicer**: Between-slider using `Price_USD`.

### E. Detailed Table View with Drill-Down & Conditional Formatting
- **Visual Type**: Table.
- **Columns**: `Title`, `Rating`, `Availability`, `Price Category`, `Price_USD`, `URL` (rendered as a hyperlink).
- **Drill-down Hierarchy**:
  Create a hierarchy named **Price Hierarchy** containing:
  1. `Price Category` (Top level)
  2. `Title` (Detail level)
  You can put this hierarchy in a Matrix visual or configure the Table visual to allow drilling down from Category groups to specific book titles.

#### Conditional Formatting Rules
Apply conditional formatting to the table to highlight key trends:
1. **High Price (Over $66 / £50)**:
   - Apply to: `Price_USD` cell background.
   - Format style: Rules.
   - Rule: If value `>= 66` and `< 99999`, set background to light red/peach (#FEE2E2) and text to dark red (#991B1B).
2. **Low Ratings (1-2 Stars)**:
   - Apply to: `Rating` cell background or text.
   - Format style: Rules.
   - Rule: If rating is `>= 1` and `<= 2`, set background to soft yellow/orange (#FEF3C7) and text to brown (#92400E).

---

## 4. Test Cases and Verification Guide

To verify the dashboard's correctness, execute the following test cases in Power BI:

| Test Case ID | Test Goal | Steps to Perform | Expected Result | Pass Criteria |
|---|---|---|---|---|
| **TC-01** | CSV Import Validation | Load CSV via Power Query and check row count. | All 1000 books are successfully read from the CSV. | Table loaded without row-loading errors. |
| **TC-02** | Data Type Validation | Inspect column data types in the Data view. | - Title, URL: Text<br>- Price_GBP, Price_USD: Decimal Number<br>- Rating: Whole Number<br>- Availability: Text | Columns have appropriate icons (e.g., summation symbol for numeric fields). |
| **TC-03** | Slicer Dynamic Update | Click Rating "5" in Slicer. Check if KPI Cards and charts update. | Visuals dynamically filter to show only 5-star books. Average price & count update correctly. | No visual errors or empty charts. |
| **TC-04** | DAX Calculation Accuracy | Verify overall average price and counts against raw stats. | - Total Books (deduplicated): 1000<br>- Average Price: $46.30<br>- % In Stock: 100% | Dashboard KPIs match source data verification. |
| **TC-05** | Category Grouping Logic | Check if books are grouped correctly into categories. | Books with Price_USD < 26.4 are "Budget", >= 26.4 & <= 66 are "Standard", > 66 are "Premium". | The Price Category column is populated without nulls. |
| **TC-06** | Conditional Formatting | Scroll through the Table view and check high price/low rating rows. | Books with Price_USD > $66 are highlighted in red; books with Rating 1 or 2 are highlighted in orange/yellow. | Colors match the defined rules. |
