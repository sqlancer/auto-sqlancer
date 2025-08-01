#!/bin/bash
set -e

echo ">> Initializing database at ${PG_DATADIR}"
if [ ! -s "${PG_DATADIR}/PG_VERSION" ]; then
    su -s /bin/bash -c "${PG_BASE}/bin/initdb -D ${PG_DATADIR}" ${PG_USER}

    echo ">> Configuring postgresql.conf and pg_hba.conf"

    echo "listen_addresses='*'" >> ${PG_DATADIR}/postgresql.conf
    echo "host all all 0.0.0.0/0 md5" >> ${PG_DATADIR}/pg_hba.conf

    # Start DB temporarily to run SQL setup
    su -s /bin/bash -c "${PG_BASE}/bin/pg_ctl -D ${PG_DATADIR} -w start" ${PG_USER}

    echo "ALTER USER ${PG_USER} WITH PASSWORD '12345678';" | su -s /bin/bash -c "${PG_BASE}/bin/psql" ${PG_USER}

    su -s /bin/bash -c "${PG_BASE}/bin/pg_ctl -D ${PG_DATADIR} -m fast stop" ${PG_USER}
fi

echo ">> Starting PostgreSQL..."
exec su -s /bin/bash -c "${PG_BASE}/bin/postgres -D ${PG_DATADIR}" ${PG_USER}
