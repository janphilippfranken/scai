# task:
# buyer prompt stage 1:
    # go and pick object (apple, orange)
    # cost: d(object)
    # reward: r(object)
    # immediate utility: U,B,1 from item i1 in {apple, orange} equals reward - cost (r(i,1) - d(i,1))

    # seller observes the buyer's choice and knows the travel cost

# seller prompt stage 2:
    # use observations from stage one to set price for future purchase of one of the two items m(i,3)
    # this requires inferences over buyer's preferences from observed action (selection of one item) such that prices are set in a way to maximise seller's reward/utility
    # this requires model of buyer's behavior

# buyer prompt stage 3:
    # buyer purchases one of the items for a price m(i,3) and then consumes it
    # again receives reward r(i,3), and utility now is U,B,3 = r(i,3) - m(i,3) 

# discounted accumulated utility is as follows
# buyer: U(i1, i3, d, m) = U,B,1(i1, d(i1)) + U,B,3(i3, m(i3)) 
# seller: U,S(i3) = m(i3)

# d(i1) is set by environment
# m(i3) is set by seller
# preferences sum to 10, walking distances sum to 10, and prices sum to 10