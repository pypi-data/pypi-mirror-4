.. _migrate-latest:

Migrate from Camelot 12.06.29 to 13.04.13
=========================================

 * Replace all imports from `elixir` with import from `camelot.core.orm`.
   This should cover most use cases of Elixir, use cases that are not
   covered in the new module (inheritance, elixir extensions) should be
   rebuild using Declarative.  Notice that it is still possible to continue
   using Elixir, but not encouraged.  This is a good time to move your code
   base over to Declarative.
   
 * If the `embedded=True` field attribute is in use, this should be removed, as
   it is no longer supported.  The proposed alternative is to use the 
   :meth:`camelot.admin.object_admin.ObjectAdmin.get_compounding_objects` method
   on the admin to display multiple objects in the same form.
   
 * Database migration commands for the changed batch job model::
 
       CREATE TABLE `batchjob_status` (
         `status_datetime` date DEFAULT NULL,
         `status_from_date` date DEFAULT NULL,
         `status_thru_date` date DEFAULT NULL,
         `from_date` date NOT NULL,
         `thru_date` date NOT NULL,
         `classified_by` int(11) NOT NULL,
         `id` int(11) NOT NULL AUTO_INCREMENT,
         `status_for_id` int(11) NOT NULL,
         PRIMARY KEY (`id`),
         KEY `status_for_id` (`status_for_id`),
         KEY `ix_batchjob_status_classified_by` (`classified_by`),
         CONSTRAINT `batchjob_status_ibfk_1` FOREIGN KEY (`status_for_id`) REFERENCES `batch_job` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
       );
       ALTER TABLE `batch_job` DROP COLUMN `status`;

  * Database migration commands for the changed authentication model::
  
      CREATE TABLE authentication_group
      (
        name character varying(256) NOT NULL,
        id serial NOT NULL,
        CONSTRAINT authentication_group_pkey PRIMARY KEY (id )
      )
   
      CREATE TABLE authentication_group_member
      (
        authentication_group_id integer NOT NULL,
        authentication_mechanism_id integer NOT NULL,
        CONSTRAINT authentication_group_member_pkey PRIMARY KEY (authentication_group_id , authentication_mechanism_id ),
        CONSTRAINT authentication_group_members_fk FOREIGN KEY (authentication_group_id)
            REFERENCES authentication_group (id) MATCH SIMPLE
            ON UPDATE NO ACTION ON DELETE NO ACTION,
        CONSTRAINT authentication_group_members_inverse_fk FOREIGN KEY (authentication_mechanism_id)
            REFERENCES authentication_mechanism (id) MATCH SIMPLE
            ON UPDATE NO ACTION ON DELETE NO ACTION
      )
      
      CREATE TABLE authentication_group_role
      (
        role_id serial NOT NULL,
        group_id integer NOT NULL,
        CONSTRAINT authentication_group_role_pkey PRIMARY KEY (role_id , group_id ),
        CONSTRAINT authentication_group_role_group_id_fkey FOREIGN KEY (group_id)
            REFERENCES authentication_group (id) MATCH SIMPLE
            ON UPDATE CASCADE ON DELETE CASCADE
      )