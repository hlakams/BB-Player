# module imports - all other imports done there
import dealer
import attendant
import benchmark
import bb_player
# import plotter

# external libraries
import warnings
import pandas as pd

# silence misc warnings
warnings.filterwarnings(action='ignore', category=RuntimeWarning)
warnings.filterwarnings(action='ignore', category=pd.errors.PerformanceWarning)

# alias for agent names
names = attendant.names

# maintain running count of results
results = [["", 0, 0, 0, 0, 0.0, 0.0] for _ in names]

# maximum batch, game runs
batch_runs = 10
num_games = 100

# base balance
base_balance = 1000.00

# initialize dataframe
df_balance = pd.DataFrame(0, index=range(batch_runs * num_games), columns=names)

# play some games of blackjack
# play this many batches of games (new deck for each batch)
for batch_no in range(batch_runs):
    # new batch
    batch_no += 1

    # initialize deck
    deck = dealer.generate_deck_distribution()

    # play X# games with a stable deck
    for name_idx, name in enumerate(names):
        # let user know current epoch
        print(f"Playing agent {name}, batch #{batch_no}")

        # base wager as a decimal float
        balance = base_balance
        wager = 10.00

        # keep track of game results
        wins = 0
        losses = 0
        draws = 0
        
        # special case for bb-player: update HMM vars
        if name == "bb":
            # transition matrix
            benchmark.transitions = bb_player.init_transitions()
            # emissions matrix
            benchmark.emissions = bb_player.init_emissions()
        
        # action procedures for all games
        for game in range(num_games):
            # resample deck distribution
            shuffled_deck = dealer.shuffle_deck(deck)
            # subsample of drawn deck
            shoe = dealer.draw_shoe(shuffled_deck)
            # conduct a new game and memoize result
            result = attendant.basic_game(shoe, wager, name)

            # decompose the result tuple
            [winning_hand, wager_outcome, status] = result
            # update running balance for agent
            balance += wager_outcome

            # add current balacne multiplier to running df
            df_balance.loc[(batch_no - 1) * num_games + game, name] = balance / base_balance

            # loss
            if status == 4:
                losses += 1
            # win
            elif status == 5:
                wins += 1
            # draw
            else:
                draws += 1

        # calculate win likelihood
        win_likelhood = (2 * wins + draws) / (2 * num_games)

        # store result
        current_result = [name, num_games, wins, losses, draws, win_likelhood, balance]
        # previous (running) result
        previous_result = results[name_idx]
        # strategy contents updated with benchmark result
        results[name_idx] = benchmark.update_results(previous_result, current_result, batch_no)

        print(df_balance.head())

    # newline for console formatting
    print('\n')

# show results
print(results)

# # show plot of running balance
# plotter.plot_running_balance(df_balance, names)

# save running balance df
df_balance.to_csv('running_balance.csv')