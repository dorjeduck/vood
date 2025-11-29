# Hole Matching Strategies

When morphing shapes with different numbers of holes (e.g., 5 holes → 2 holes), Vood needs to decide which holes merge together or split apart. This document explains the available strategies and how to configure them.

## Available Strategies

### 1. Clustering (Default) ⭐

**Best for:** Visual quality and balanced morphing

Uses k-means spatial clustering to group holes into balanced clusters, ensuring roughly equal numbers of holes merge/split at each destination.

**Algorithm:**
- For N→M merging: Clusters N source holes into M groups
- For N→M splitting: Clusters M destination holes into N groups
- Uses k-means++ initialization for better results
- Optional post-processing to balance cluster sizes

**Example:** 5 holes → 2 holes produces a **2-3 split** instead of 4-1

**Configuration:**
```toml
[morphing]
hole_mapper = "clustering"

[morphing.clustering]
balance_clusters = true      # Enforce balanced sizes (recommended)
max_iterations = 50          # Convergence iterations
random_seed = 42             # For reproducible results
```

### 2. Greedy

**Best for:** Speed and simplicity

Uses fast nearest-centroid matching. Each hole independently finds its closest destination.

**Algorithm:**
- For N→M merging: Each source finds nearest destination
- For N→M splitting: Each destination finds nearest source
- O(n²) time complexity, very fast

**Warning:** May produce unbalanced results (e.g., 4-1 splits) depending on hole positions.

**Configuration:**
```toml
[morphing]
hole_mapper = "greedy"
```

### 3. Hungarian (Not Yet Implemented)

**Best for:** Optimal assignment

Would use the Hungarian algorithm to find the globally optimal matching that minimizes total distance.

**Configuration:**
```toml
[morphing]
hole_mapper = "hungarian"  # Will raise NotImplementedError
```

---

## Configuration

### Using vood.toml

Create a `vood.toml` file in your project directory:

```toml
[morphing]
# Choose strategy: "clustering", "greedy", or "hungarian"
hole_mapper = "clustering"

[morphing.clustering]
# Clustering-specific options
balance_clusters = true
max_iterations = 50
random_seed = 42
```

### Programmatic Override

Override the strategy in code:

```python
from vood.transition.interpolation.align_vertices import get_aligned_vertices
from vood.transition.interpolation.hole_matching import GreedyNearestMapper

# Use greedy matcher for this specific alignment
contours1, contours2 = get_aligned_vertices(
    state1, state2,
    hole_mapper=GreedyNearestMapper()
)
```

Or with custom clustering parameters:

```python
from vood.transition.interpolation.hole_matching import ClusteringMapper

# Custom clustering settings
matcher = ClusteringMapper(
    balance_clusters=True,
    max_iterations=100,
    random_seed=123
)

contours1, contours2 = get_aligned_vertices(
    state1, state2,
    hole_mapper=matcher
)
```

---

## Examples

### Balanced Clustering (Recommended)

```toml
[morphing]
hole_mapper = "clustering"

[morphing.clustering]
balance_clusters = true
```

**Result:** 5 holes → 2 holes produces 2-3 or 3-2 split

### Pure K-Means (No Balancing)

```toml
[morphing]
hole_mapper = "clustering"

[morphing.clustering]
balance_clusters = false
```

**Result:** May produce 1-4 or 4-1 splits if geometrically optimal

### Fast Greedy

```toml
[morphing]
hole_mapper = "greedy"
```

**Result:** Fast but may be unbalanced (1-4, 4-1 splits possible)

---

## Visual Comparison

Using the example from `examples/y.py`:

**Hole Configuration:**
- **State A (5 holes):** Cross pattern at (0,0), (-50,0), (50,0), (0,-50), (0,50)
- **State B (2 holes):** Diagonal pattern at (-70,-70), (70,70)

**Results:**

| Strategy | Balance | Split | Visually Balanced? |
|----------|---------|-------|-------------------|
| Clustering (balanced) | 1 | 2-3 or 3-2 | ✅ Yes |
| Greedy | 3 | 1-4 or 4-1 | ⚠️ No |
| Clustering (unbalanced) | 3 | 1-4 or 4-1 | ⚠️ No |

---

## When to Use Each Strategy

### Use Clustering (Balanced) when:
- Visual quality matters
- You want smooth, balanced morphing
- Holes are morphing between similar counts (2↔3, 3↔5, etc.)
- **This is the default and recommended choice**

### Use Greedy when:
- Speed is critical
- Simple morphing is acceptable
- Hole positions naturally form balanced groups
- Prototyping/testing

### Use Clustering (Unbalanced) when:
- You want pure k-means behavior
- Testing/experimenting with different clustering results
- Specific artistic effect desired

---

## Testing Your Configuration

Run the diagnostic tests to see strategy differences:

```bash
# Test merging balance (5→2)
python examples/test_hole_clustering.py

# Test splitting balance (2→5)
python examples/test_hole_splitting.py

# Test config selection
python examples/test_config_matcher.py
```

---

## Technical Details

### Balanced Clustering Algorithm

1. **Initial Clustering:** Run k-means on hole centroids
2. **Balance Check:** Calculate ideal cluster size (n/k)
3. **Rebalancing:** If imbalance > 40% of ideal:
   - Find largest and smallest clusters
   - Move points from large to small clusters
   - Choose points closest to target cluster centroid
   - Repeat until balanced (difference ≤ 1)

### Performance

- **Clustering:** O(n·k·i) where i = iterations (typically 5-10)
- **Greedy:** O(n²)
- **Balancing:** O(n²) in worst case, usually O(n·k)

For typical hole counts (2-10 holes), all strategies are fast (<1ms).

---

## Future Enhancements

Planned improvements:

1. **Hungarian Algorithm:** Optimal assignment with capacity constraints
2. **User-Specified Matching:** Manual hole correspondence override
3. **Hierarchical Clustering:** Alternative to k-means
4. **Spatial Bisection:** Balanced partition via recursive space splitting

---

## See Also

- `vood/transition/interpolation/hole_matching/` - Implementation
- `vood/config/defaults.toml` - Default configuration
- `CLAUDE.md` - Architecture documentation
- `examples/perforated_astroid_test.py` - Shape with multiple holes
