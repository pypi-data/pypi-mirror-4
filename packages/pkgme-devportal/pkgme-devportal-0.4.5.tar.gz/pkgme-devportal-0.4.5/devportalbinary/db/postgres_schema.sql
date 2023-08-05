CREATE TABLE IF NOT EXISTS libdep (
    source_package_name TEXT,
    library TEXT,
    dependency TEXT,
    CONSTRAINT libdep_uniq UNIQUE (
        source_package_name, library, dependency)
);
