# Pycord v3 Contribution Guide

This is an extremely basic guide for contributing to the repo.

## Steps for Every Contribution

***There is only 1.***

1. Make sure your contribution is not a duplicate before opening (i.e., search all open contributions and ensure it doesn't closely relate to yours).

## Steps for Opening Issues

Thanks for taking the time to open an issue, this helps us make a more stable and usable library.

1. Fill out the template. If the template is not filled out properly, your issue will most likely be closed.
   1. If you include a traceback when creating a bug report, or if you include bits of code in your feature request, please place it in a [code block](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-and-highlighting-code-blocks).
2. Be as detailed as possible when creating your issue. In most scenarios, the fewer details that we are given, the longer it will take for your issue to be resolved.

## Steps for Opening Pull Requests

Considering that we are in a pre-alpha state right now, thank you very much for your contribution. It is deeply appreciated.

However, before you create your PR, please ensure you've done a couple of things:

1. Your PR needs to have a clear purpose. PRs that edit multiple files are more than welcome, but make sure it accomplishes a single goal. This could be fixing a bug, refactoring, or even adding new material.
2. Follow the style of the library. This implies two separate points:
   1. Make sure your code is as clean as possible and looks similar to the rest of the codebase. This includes spacing, function signatures/definitions, and commenting/documentation format.
   2. Ensure that your opened pull request follows the [Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/#summary) styling guide. This helps people understand the purpose of the PR, and how it should be reviewed.
3. If possible, try to use our pre-commit hooks to format your code. These hooks format the code before you push it to GitHub, and could vastly improve your own experience by not needing to use other formatting commands.

## Appending to the Changelog

Pycord tries to keep an up-to-date changelog of every change to ensure easy tracking of breaking or non-breaking changes.

This does mean however that you need to changelog every pull request you make.
We try to make this as easy as possible to ensure *you* the developer can easily make and get a pull request merged.

Firstly, if you haven't already, download Towncrier (the tool we use for changelog upkeep):

```sh
pip install -U towncrier
```

Now, you are ready to create the house of your change, its file. To start:

```sh
towncrier create {pull_request_shortname}.{pull_request_number}.{pull_request_type}
```

This command means multiple things, in which:

- `pull_request_shortname`: the name of your PR lowercased and in the shortest form possible.
- `pull_request_number`: the pull request your making this for. i.e.: #178
- `pull_request_type`: the type of pull request (doc, feature, removal, bug, trivial, etc).

Once you've formed that, you can make the content of your changelog. There's are not too much rules about what you *can* and *can't*
put in this. Of course, they have to be relevant to the pull request, however, they do have to have one general form:

```md
[#{pull_request_number}](https://github.com/pycord/pycord-v3/issues/{pull_request_number}): {pull_request_name}

{Details on what this pull request does, and why}

- {An exact}
- {List of}
- {Changes}
```

This only introduces one notable variable: `{pull_request_name}`.

This variable is simply a version of your pull request name without Conventional Commits. Such as:

- "Adds Towncrier"
- "Implement Modals"
- "Switch to Ruff," etc..

## Where can I get more help with my issue/PR?

Docs are somewhat chaotic at the moment, so your best bet is [our Discord server](https://discord.gg/pycord).
