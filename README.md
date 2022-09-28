# Valorant Stats
This project started because I wanted to know my [KAST metric](https://www.thespike.gg/forums/topic/introducing-kast-metric/9703) for my ranked games in Valorant. The purpose for this project is primarily to brush up on Python (e.g. working with type annotations), practice working with virtual environments, and to have a bit of fun with data and statistics.

## Technical Details
This project uses [raimannma's Valorant API wrapper](https://github.com/raimannma/ValorantAPI) to get the data.

Note that at the time of this writing, the API currently does not provide data on ability casts per round (all of the values are `None`), so the KAST calculator does not account for corner cases where Sage's resurrection is involved. I will update this calculation at a future time when the API provides the necessary data.
