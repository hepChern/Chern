$ wget https://raw.githubusercontent.com/reanahub/reana/maint-0.9/etc/kind-localhost-30443.yaml
# $ kind create cluster --config kind-localhost-30443.yaml
# change to
kind create cluster --config kind-localhost-30443.yaml --image kindest/node:v1.25.11@sha256:227fa11ce74ea76a0474eeefb84cb75d8dad1b08638371ecf0e86259b35be0c8
$ wget https://raw.githubusercontent.com/reanahub/reana/maint-0.9/scripts/prefetch-images.sh
$ sh prefetch-images.sh
$ helm repo add reanahub https://reanahub.github.io/reana
$ helm repo update
$ helm install reana reanahub/reana --namespace reana --create-namespace --wait




NAME: reana
LAST DEPLOYED: Sun Aug  6 16:25:36 2023
NAMESPACE: reana
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
The REANA system has been installed!

If you are upgrading from a previous REANA release series, you may need to
upgrade database schema now:

   $ kubectl -n reana exec -i -t deployment/reana-server -c rest-api -- reana-db alembic upgrade

Please see the dedicated upgrade documentation at
<https://docs.reana.io/administration/deployment/upgrading-db/>

If you are deploying REANA for the first time, there are a few steps left to
finalise its configuration.

1. Initialise the database:

    $ kubectl -n reana exec deployment/reana-server -c rest-api -- \
        ./scripts/create-database.sh

2. Create administrator user and corresponding access token:

    $ mytoken=$(kubectl -n reana exec deployment/reana-server -c rest-api -- \
          flask reana-admin create-admin-user --email john.doe@example.org \
                                              --password mysecretpassword)

3. Store administrator access token as Kubernetes secret:

    $ kubectl -n reana create secret generic reana-admin-access-token \
        --from-literal=ADMIN_ACCESS_TOKEN="$mytoken"

4. Try to run your first REANA example:

    $ firefox https://localhost:30443

   Or, using command line:

    $ # install REANA client
    $ pip install --user reana-client
    $ # set environment variables for REANA client
    $ export REANA_SERVER_URL=https://localhost:30443
    $ export REANA_ACCESS_TOKEN="$mytoken"
    $ # test connection to the REANA cluster
    $ reana-client ping
    $ # clone and run a simple analysis example
    $ git clone https://github.com/reanahub/reana-demo-root6-roofit
    $ cd reana-demo-root6-roofit
    $ reana-client run -w demo



------------------------------------------------------------------------
# List users
kubectl -n reana exec deployment/reana-server -c rest-api -- \
          flask reana-admin user-list --admin-access-token i8puUFC3jOvvzsPAjkkH8g

# Create user
kubectl -n reana exec deployment/reana-server -c rest-api -- flask reana-admin user-create --email local@chern.org --admin-access-token i8puUFC3jOvvzsPAjkkH8g
User was successfully created.
ID                                     EMAIL             ACCESS_TOKEN
2357d6b5-30c6-4598-82f6-d5566538022c   local@chern.org   NHo5MQHPzDp9H2fVpzUdRA


