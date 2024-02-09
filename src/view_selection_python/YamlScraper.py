class YamlScraper:
    """For now, read contents of the profiles.yml file.
    I should, however, check out which exact info I need,
    because it is unclear to me at this exactly how dbt decides where to write to
    (see also notion, the tool -> variables to set -> profiles.yml)"""
    pass

    def read_contents(self):
        """Read the contents of a yaml file"""
        pass

    def extract_db_creds(self):
        """Return the credentials of the db host, dbname, schema where the
        view_selection_tool tables are written to"""
        pass
