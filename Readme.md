# 設定檔說明

```config
[default]
input_file = patent_id
output_directory = result

[setting]
endpoint = patents
input_type = patent_number 
fields = ["patent_number","patent_title", "patent_abstract", "patent_num_claims", "patent_num_combined_citations", "cited_patent_number","citedby_patent_number","assignee_id","assignee_organization","assignee_first_name","assignee_last_name","assignee_country"]

[filter]
date_range = ["2000-01-01", "2020-06-01"]
sort = [{"patent_number": "asc"}, {"patent_title":"desc"}]
```

* 必須欄位 `defalut`、`setting`
* 篩選欄位(可有可無) `filter`

`input_file`: id 的文字檔
`output_directory`: 結果檔案輸出的資料夾 ( 預設當前目錄 ) 
