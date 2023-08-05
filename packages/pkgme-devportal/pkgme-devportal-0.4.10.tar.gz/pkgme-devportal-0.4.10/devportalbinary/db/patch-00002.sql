ALTER TABLE libdep
  ALTER COLUMN architecture SET NOT NULL;

-- also update the unique constraint

ALTER TABLE libdep
  DROP CONSTRAINT libdep_uniq;

ALTER TABLE libdep
  ADD CONSTRAINT libdep_uniq
  UNIQUE (source_package_name, library, dependency, architecture);
