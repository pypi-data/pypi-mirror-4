import random

def _weighted_shuffle(weight_item_pairs,prng=random):
    """Shuffle items from weight_item_pairs using weights"""
    pairs = [pair for pair in weight_item_pairs]
    pairs.sort(key=lambda pair: pair[0])
    total = sum(pair[0] for pair in pairs)

    choices = []
    for i in range(len(pairs)):
        # Detect a one-length array and take a shortcut
        if len(pairs) == 1:
            choices.append(pairs.pop(0)[1])
            return choices

        # Choose a score
        score = prng.randint(0, total-1)

        # Find the item the score selected
        for j in range(len(pairs)):
            score -= pairs[j][0]
            if score < 0:
                # Add the choice to the choices list
                choice = pairs.pop(j)
                choices.append(choice[1])

                # Update the PRNG ceiling
                total -= choice[0]
                break

    # This line should not be reached
    assert False, "The loop should have already returned."

def find_text(service, zone=None):
    """Return a TXT record for the specified service and zone"""
    import dns.resolver
    service_name = service if zone is None else service + '.' + zone + '.'
    results = dns.resolver.query(service_name, 'TXT')
    text = None

    for record in results:
        text = record.strings[0]
        break

    return text

def find_service(service, zone=None):
    """Return a properly-weighted try list of servers for the specified zone"""
    import dns.resolver
    service_name = service if zone is None else service + '.' + zone + '.'
    results = dns.resolver.query(service_name, 'SRV')

    # Group results by priority
    by_priority = {}
    for record in results:
        p_list = by_priority.setdefault(record.priority, [])
        p_list.append(record)

    # Weighted-random sort each priority tier
    choices = []
    for priority in sorted(by_priority.keys()):
        # Prepare the p_list for a weighted shuffle
        p_list = by_priority[priority]
        pairs = [(record.weight, (record.target.to_text(), record.port)) for record in p_list]

        # Add shuffled results to the choices list
        choices += _weighted_shuffle(pairs)

    return choices
