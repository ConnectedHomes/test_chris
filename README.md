# ukh-aws-ci-web

CI stack for British Gas (Ember) web apps

<details>
  <summary>
    CI flow diagram
  </summary>
  <br>

  See updated version [in here](https://github.com/ConnectedHomes/ngw-infrastructure/blob/master/docs/CI%20flow.png)

  ![CI flows](https://github.com/ConnectedHomes/ngw-infrastructure/blob/master/docs/CI%20flow.png)
</details>

## Github App ukh-aws-ci-web-webhook

As many different repos need to consume the webhook provided by this Stack, the corresponding configuration has been moved away from each repo's setting and into its [own github App](https://github.com/organizations/ConnectedHomes/settings/apps/ukh-aws-ci-web-webhook).
* If needed (probably not), change the **production** webhook URL in this github App
* Add this app to your repo if you want to use the CI provided by this stack.

## Shared Stack

Refer to [shared stack wiki](https://github.com/ConnectedHomes/shared-devops-ci-step-functions/blob/main/README.md).

## Stages

### Stages overview

* Each stage deploys its own S3 buckets, cloudformation stacks, lambdas, and [API gateways](https://eu-west-1.console.aws.amazon.com/apigateway/main/apis?region=eu-west-1), all of them having your stage value in their names.
* When creating a new stage, you will create a new webhook. Add the [corresponding URL](https://eu-west-1.console.aws.amazon.com/apigateway/home?region=eu-west-1#/apis/386cbuqh62/stages/prod/resources/~1apiResource/methods/POST) to your repo webhook settings **only once, and then you shouldn't need to change anything on the repo** (ask a github admin for that, Lionel or Shilpa).
* The stage logic allows to consume several stages for the same repo without disturbing the workflow of the developers who keep consuming normally the "prod" stage on their branches.
* The logic is the following:
  *  branch names containing the string "stage-{StageName}" will trigger the flow of the corresponding stage stack
  *  other branches will be ignored for this stage, except for the "prod" stage that will work with all branches except those with format "stage-XX".


### Creating a new Stage

Change:

* the [STAGE_NAME environment variable](https://eu-west-1.console.aws.amazon.com/codesuite/codebuild/projects/ukh-aws-ci-web/edit/environment?region=eu-west-1) to the name of your stack (typically, use your name: biplav, lionel or shilpa)
* start build
* Add the webhook to the repo(s) you want to test as per previous section.

### Updating an existing Stage

* the [buildspec path](https://eu-west-1.console.aws.amazon.com/codesuite/codebuild/projects/ukh-aws-ci-web/edit/buildspec?region=eu-west-1) to digital_Web_CI_Stack/buildspec_update.yml
* the [STAGE_NAME environment variable](https://eu-west-1.console.aws.amazon.com/codesuite/codebuild/projects/ukh-aws-ci-web/edit/environment?region=eu-west-1) to the name of your stack (typically, use your name: biplav, lionel or shilpa)
* start build

## Other WebApps DevOps repos

Other repos which are using to setup the pipelines:

   https://github.com/ConnectedHomes/ngw-codebuild-utils
    This repo contains all the scripts used for WebApps, MicroServices and Test-Automation pipelines.

   https://github.com/ConnectedHomes/ngw-apps-edge-router-fn
    Lambda edge router function for web apps.

   https://github.com/ConnectedHomes/ngw-edge-redirect-fn
    Handling redirects on a CloudFront default behaviour

  https://github.com/ConnectedHomes/ngw-web-apps-edge-response-fn
  https://github.com/ConnectedHomes/ngw-apps-edge-response-fn
    For Canary releases

   https://github.com/ConnectedHomes/ngw-cf-cloudfront
    CloudFront configuration for FE apps

   https://github.com/ConnectedHomes/ngw-ado-release-trigger
    This to trigger web-app deployment pipeline in AzureDevOps

   https://github.com/ConnectedHomes/bg-devops-ado/tree/master/src/pipelines/web-app-release
    This is triggered in [ADO jobs](https://dev.azure.com/Centrica-Digital/Digital-DevOps/_release?_a=releases&view=mine&definitionId=58)

More infos on [web playbook](https://playbook.digital/product-engineering/continuous-integration)

## Tests

All the linting and test commands are defined in https://github.com/ConnectedHomes/digital-DevOps/.github/workflows/python-app.yml

### linting

* Add `pylint` package to your IDE

* run linting checks with `py.test --pylint -m pylint --pylint-error-types=EF -v`

### running tests

Run `coverage run --source . -m run_tests.py` locally.

### adding a debugger

```python3
import pdb
pdb.set_trace()
```

Then run `python3 run_tests.py`, _et voilà!_

## Use as a template

This repo has been setup as a github template, to allow creating other parent stacks easily

### Create a new parent stack

Click on ["Use this template"](https://github.com/ConnectedHomes/ukh-aws-ci-web)

### Pull changes from the template

```sh
git remote add template https://github.com/ConnectedHomes/ukh-aws-ci-web.git
git fetch --all
git merge template/branch-name-you-want-to-merge --allow-unrelated-histories
```
