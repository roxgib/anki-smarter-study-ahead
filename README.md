# Smarter Study Ahead
An add-on for Anki that generates filtered decks for studying ahead

## Introduction
Studying ahead (i.e. studying cards today that should be due tomorrow or over the next few days) is a useful tool for any serious Anki user, allowing you to balance your study load, make use of extra time or energy you happen to have, or just give yourself a day off without the reviews stacking up. Unfortunately, studying ahead is suboptimal because some cards will have intervals that are too short, and studying them early can significantly change the interval. This add-on tries to address that problem.

Smarter Study Ahead creates filtered decks by selecting the most optimal cards for studying ahead. It does this by selecting the cards for which studying them today would reduce the interval by the smallest percentage amount. For example, if a card due tomorrow has an interval of 20 days, studying it today would reduce the interval by 5% (i.e. by 1 day out of 20). If another card due in 2 days has an interval of 100 days, studying it today would reduce the interval by 2% (i.e. by 2 days out of 100). If you have time today to only study one extra card, the second card is the better choice, even though it's due two days from now, because the effect on its interval is much smaller.

## Usage
To use this addon, simply click the cog next to a deck and select 'Study Ahead'. A filtered deck will be created containing the most optimal cards for studying ahead.  

By default only the most optimal 100 cards will be chosen - to study ahead further, simply click 'Study Ahead' again to fill the deck with the next set of cards. 

## Settings
You can change the following settings in the add-on config to affect the limits that are placed on what cards to choose:

"max_days_ahead": card will only be chosen for study ahead if they are due for review within this amount of days. Default is 7 days. 

"max_cards": this is the maximum number of cards that will be chosen for each filtered deck. Once you've studied them, creating a new filtered deck may find new cards to study ahead. Set this to a high number if you just want all the eligible cards to appear the first time around.

"max_multiple": This is the maximum ratio between how far ahead a card is and its interval. The default is 10. This means if a card is due tomorrow, it must have an interval of at least 10 days to be eligible to be studied ahead. If it's due in 2 days, it must have an interval of at least 20 days, and so on. Changing the number of 5 would mean that tomorrow's cards would be chosen if they have an interval of at least 5, cards due in 2 days must have an interval of at least 10 days, and so on. Don't set this value too low - the point of this add-on is to choose the cards for which studying ahead will have the least impact. For mature decks, most cards should be eligible with this settings left on its default value of 10, so you probably don't need to change this setting.

## Bugs, problems, feature requests
Please posts these to the GitHub issue tracker - don't leave them in a review on the Anki site or a Reddit comment etc because I might not see it.

## FAQ
**Does this mess with the scheduling algorythm?** - Not directly - all it does is create filtered decks, and uses Anki's built-in system for determining the interval of early reviews, so it's not messing with Anki's underlying scheduling algorythm.

**How will this affect the new intervals of the studied cards?** - See <a href=https://docs.ankiweb.net/filtered-decks.html#reviewing-ahead>this page</a> from the Anki Manual, but the short answer is 'not much' since the intervals are only changing by a maximum of 10% on the default settings, and usually by much less than this. From the manual:

> If the cards were almost due to be shown, they will be given a new delay similar to what they would have received if you had reviewed them on time.

**The Anki Manual warns against the repeated use of the review ahead feature. Does this apply to this addon as well?** - No. This addon is designed to addess the limitations of the builtin 'review ahead' feature so you can use it every day if you want.