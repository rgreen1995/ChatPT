# ChatPT

## TLDR 
ChatPT is an AI-powered fitness app built for generating and managing personalised workout and nutrition plans through conversational consultations.

It is designed first and foremost as a **personal tool** — something highly specific that I personally want to use. 

It was also an experiment in using **AI agents to build software**. ~ 90% of the codebase was written by AI. (including this README)

It is **not intended for commercialisation** and will remain **open source** (Other than in the unlikely event that someone offers me a **lot** of money).


## What the app does

ChatPT helps users:

- create personalised **training plans** through an AI consultation flow
- create personalised **nutrition plans** through a separate AI consultation flow
- save and revisit plans
- track workout progress over time
- browse an exercise library with instructions and video links
- request missing exercises for future addition
- manage user accounts and authentication

The app aims to make plan creation feel conversational rather than form-heavy.

## Why this project exists
I originally found myself using AI chatbots to generate training programmes, then manually transferring those programmes into apps like Strong for logging and in-workout features. After doing that enough times, it became obvious that this middle step shouldn’t exist. If AI can write the programme, it should also be able to deliver it, track it, adapt it, and support you while you actually train.

Cost is the other major reason this project exists. Good coaching and nutrition advice is expensive — often **£30 to £200+ a month**, and sometimes far more. That pricing makes sense in the old model, where access to useful knowledge and personal attention was limited. It makes far less sense now that a large amount of that knowledge is already available through high-end AI systems.

AI also does a number of things which are objectively better by default. It is available **24/7**, it does not lose patience, it does not forget context, and it is completely **judgement-free**. You can ask basic questions, ask the same question five times, change your goals halfway through, or need help at 11pm, and none of that is an issue. For many people, that already makes it a safer space and more useful than a traditional coach.

Realistically with the current models I do think AI should replace most online human fitness coaches. If this is not currently true then it will definitely be true within a year or two.

Not because good coaches have no value, but because for the vast majority of people the current model is expensive, inconsistent, hard to access, and often not nearly as personalised as it claims to be. A genuinely well-built AI system should be able to give better guidance, more consistently, at effectively zero marginal cost, and be available in your pocket whenever you need it.

That is the long-term aim of this project: to help build a fitness assistant that is **free, better, and always available**. Something more useful than a coach you have to book, pay monthly for, and wait to hear back from. Something that can eventually give ordinary people access to a level of support that would previously have been unavailable at any price.



### Another (less philiosophical) reason why this project existst
This project was also an experiment in using **AI agents to build software**.

A very large proportion of the codebase — close to **99%** — was written by AI. The goal was to explore how far AI-assisted development could go when building a very specific app for a real personal use case.

So this repository is both:

- a usable application
- an experiment in AI-driven software development

That said, the project is still maintained with human judgment, review, and direction.

## Project status

This is an active open-source personal project.

Please assume:

- features may evolve quickly
- structure may be refactored over time
- some implementation details are still experimental
- contributions are welcome, but should follow the branching and PR workflow below

## Features

### Training consultation
Users can chat with an AI trainer to build structured workout plans based on:

- goals
- training experience
- equipment access
- preferred schedule
- injuries or constraints

### Nutrition consultation
Users can also chat with an AI nutrition coach to generate nutrition plans tailored to their goals and preferences.

### Saved plans
Generated workout and nutrition plans are stored and can be revisited later.

### Progress tracking
Users can log exercise performance and review progress over time.

### Exercise library
The app includes an exercise library with:

- exercise categories
- instructions
- form cues
- video links

### Missing exercise requests
If an exercise is referenced but not available in the library, the app can track that request so it can be added later.

### Flexible storage
The app supports:

- **SQLite** by default for local use
- **Supabase** when configured

## Tech stack

- **Python 3.11**
- **Streamlit**
- **Poetry**
- **SQLite** / **Supabase**
- **Anthropic / OpenAI / Gemini integrations** (depending on configuration)

## Getting started

``` markdown
## Getting started

### 1. Clone the repository
```

bash git clone <your-repo-url> cd ChatPT``` 

### 2. Install dependencies

Using Poetry:
```

bash poetry install``` 

### 3. Configure secrets

Copy the example secrets file and fill in your own values:
```

bash copy .streamlit\secrets.toml.example .streamlit\secrets.toml``` 

Then update the values in `.streamlit/secrets.toml`.

At minimum, you will typically need an AI provider API key.

### 4. Run the app
```

bash poetry run streamlit run app.py``` 

The app will usually be available at:
```

text http://localhost:8501``` 

## Configuration notes

The app supports optional integrations such as:

- AI provider configuration
- Google OAuth
- Supabase
- email delivery

If optional services are not configured, the app is designed to fall back gracefully where possible.

## Open source and intended use

This project is open source and will stay that way.

A few important expectations:

- this is a **personal-use-first** project
- it is **not being built for commercial sale**
- feature decisions may prioritise what is useful to the maintainer
- contributions are welcome when they align with the direction of the project

## Contributing

Contributions are welcome, but please follow the branching model below so reviews stay tidy and the project history stays easy to understand.

Ideally to keep with the theme of the project, contributions should be built using AI-assisted development. Ideally 
agents. It would be cool if this project could showcase the power of AI agents in software development.

### Branching strategy

For any contribution, first create a **feature branch**.

Feature branch format:
```

text <name_of_feature/feature>``` 

This branch will be moved to **WIP** immediately and acts as the parent branch for all work related to that feature.

From that feature branch, create smaller branches for each focused piece of work.

Contribution branch format:
```

text <name_of_feature/<name_of_contribution_to_feature>``` 

These smaller branches should represent one small, reviewable unit of work.

### Expected workflow

1. Create a feature branch
2. Mark that feature branch as WIP
3. Create smaller contribution branches from the feature branch
4. Open PRs from the small contribution branches into the feature branch
5. When the feature branch is in a good state, merge the feature branch into `main`

### Why this workflow?

This helps by:

- keeping PRs small and easier to review
- separating large features into clean units of work
- avoiding huge long-running branches with messy history
- making the project easier to reason about later

### Practical example

Feature branch:
```

text progress-tracking/feature``` 

Small branches off that feature:
```

text progress-tracking/add-volume-chart progress-tracking/fix-session-timer progress-tracking/improve-progress-ui``` 

Then:

- each small branch merges into `progress-tracking/feature`
- once the feature branch is ready, it merges into `main`

## Contribution guidelines

When contributing:

- keep changes focused and small
- prefer one concern per PR
- explain **why** the change is needed, not just what changed
- avoid unrelated refactors in feature PRs
- keep naming clear and descriptive
- test your changes locally before opening a PR

### PR expectations

Please include in your PR:

- a short summary of the change
- why the change is needed
- any setup or test notes
- screenshots if UI behaviour changed

### Good contribution types

Examples of good contributions:

- bug fixes
- UI improvements
- better error handling
- performance improvements
- exercise library additions
- docs improvements
- test coverage
- refactors that clearly improve maintainability

## Development notes

A few useful points for contributors:

- the app is Streamlit-based, so a lot of the UI is driven through page render functions
- workout and nutrition flows are separate, but related
- data storage may run through either SQLite or Supabase depending on configuration
- some behaviour is intentionally pragmatic rather than over-engineered — this is a personal app, not an enterprise spaceship

## License

This project is licensed under the **MIT License**.

See [LICENSE](LICENSE) for details.
```

