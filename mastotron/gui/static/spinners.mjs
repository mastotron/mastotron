function noop() { }
function run(fn) {
    return fn();
}
function blank_object() {
    return Object.create(null);
}
function run_all(fns) {
    fns.forEach(run);
}
function is_function(thing) {
    return typeof thing === 'function';
}
function safe_not_equal(a, b) {
    return a != a ? b == b : a !== b || ((a && typeof a === 'object') || typeof a === 'function');
}
function is_empty(obj) {
    return Object.keys(obj).length === 0;
}

// Track which nodes are claimed during hydration. Unclaimed nodes can then be removed from the DOM
// at the end of hydration without touching the remaining nodes.
let is_hydrating = false;
function start_hydrating() {
    is_hydrating = true;
}
function end_hydrating() {
    is_hydrating = false;
}
function upper_bound(low, high, key, value) {
    // Return first index of value larger than input value in the range [low, high)
    while (low < high) {
        const mid = low + ((high - low) >> 1);
        if (key(mid) <= value) {
            low = mid + 1;
        }
        else {
            high = mid;
        }
    }
    return low;
}
function init_hydrate(target) {
    if (target.hydrate_init)
        return;
    target.hydrate_init = true;
    // We know that all children have claim_order values since the unclaimed have been detached
    const children = target.childNodes;
    /*
    * Reorder claimed children optimally.
    * We can reorder claimed children optimally by finding the longest subsequence of
    * nodes that are already claimed in order and only moving the rest. The longest
    * subsequence subsequence of nodes that are claimed in order can be found by
    * computing the longest increasing subsequence of .claim_order values.
    *
    * This algorithm is optimal in generating the least amount of reorder operations
    * possible.
    *
    * Proof:
    * We know that, given a set of reordering operations, the nodes that do not move
    * always form an increasing subsequence, since they do not move among each other
    * meaning that they must be already ordered among each other. Thus, the maximal
    * set of nodes that do not move form a longest increasing subsequence.
    */
    // Compute longest increasing subsequence
    // m: subsequence length j => index k of smallest value that ends an increasing subsequence of length j
    const m = new Int32Array(children.length + 1);
    // Predecessor indices + 1
    const p = new Int32Array(children.length);
    m[0] = -1;
    let longest = 0;
    for (let i = 0; i < children.length; i++) {
        const current = children[i].claim_order;
        // Find the largest subsequence length such that it ends in a value less than our current value
        // upper_bound returns first greater value, so we subtract one
        const seqLen = upper_bound(1, longest + 1, idx => children[m[idx]].claim_order, current) - 1;
        p[i] = m[seqLen] + 1;
        const newLen = seqLen + 1;
        // We can guarantee that current is the smallest value. Otherwise, we would have generated a longer sequence.
        m[newLen] = i;
        longest = Math.max(newLen, longest);
    }
    // The longest increasing subsequence of nodes (initially reversed)
    const lis = [];
    // The rest of the nodes, nodes that will be moved
    const toMove = [];
    let last = children.length - 1;
    for (let cur = m[longest] + 1; cur != 0; cur = p[cur - 1]) {
        lis.push(children[cur - 1]);
        for (; last >= cur; last--) {
            toMove.push(children[last]);
        }
        last--;
    }
    for (; last >= 0; last--) {
        toMove.push(children[last]);
    }
    lis.reverse();
    // We sort the nodes being moved to guarantee that their insertion order matches the claim order
    toMove.sort((a, b) => a.claim_order - b.claim_order);
    // Finally, we move the nodes
    for (let i = 0, j = 0; i < toMove.length; i++) {
        while (j < lis.length && toMove[i].claim_order >= lis[j].claim_order) {
            j++;
        }
        const anchor = j < lis.length ? lis[j] : null;
        target.insertBefore(toMove[i], anchor);
    }
}
function append(target, node) {
    if (is_hydrating) {
        init_hydrate(target);
        if ((target.actual_end_child === undefined) || ((target.actual_end_child !== null) && (target.actual_end_child.parentElement !== target))) {
            target.actual_end_child = target.firstChild;
        }
        if (node !== target.actual_end_child) {
            target.insertBefore(node, target.actual_end_child);
        }
        else {
            target.actual_end_child = node.nextSibling;
        }
    }
    else if (node.parentNode !== target) {
        target.appendChild(node);
    }
}
function insert(target, node, anchor) {
    if (is_hydrating && !anchor) {
        append(target, node);
    }
    else if (node.parentNode !== target || (anchor && node.nextSibling !== anchor)) {
        target.insertBefore(node, anchor || null);
    }
}
function detach(node) {
    node.parentNode.removeChild(node);
}
function destroy_each(iterations, detaching) {
    for (let i = 0; i < iterations.length; i += 1) {
        if (iterations[i])
            iterations[i].d(detaching);
    }
}
function svg_element(name) {
    return document.createElementNS('http://www.w3.org/2000/svg', name);
}
function text(data) {
    return document.createTextNode(data);
}
function empty() {
    return text('');
}
function attr(node, attribute, value) {
    if (value == null)
        node.removeAttribute(attribute);
    else if (node.getAttribute(attribute) !== value)
        node.setAttribute(attribute, value);
}
function children(element) {
    return Array.from(element.childNodes);
}

let current_component;
function set_current_component(component) {
    current_component = component;
}

const dirty_components = [];
const binding_callbacks = [];
const render_callbacks = [];
const flush_callbacks = [];
const resolved_promise = Promise.resolve();
let update_scheduled = false;
function schedule_update() {
    if (!update_scheduled) {
        update_scheduled = true;
        resolved_promise.then(flush);
    }
}
function add_render_callback(fn) {
    render_callbacks.push(fn);
}
let flushing = false;
const seen_callbacks = new Set();
function flush() {
    if (flushing)
        return;
    flushing = true;
    do {
        // first, call beforeUpdate functions
        // and update components
        for (let i = 0; i < dirty_components.length; i += 1) {
            const component = dirty_components[i];
            set_current_component(component);
            update(component.$$);
        }
        set_current_component(null);
        dirty_components.length = 0;
        while (binding_callbacks.length)
            binding_callbacks.pop()();
        // then, once components are updated, call
        // afterUpdate functions. This may cause
        // subsequent updates...
        for (let i = 0; i < render_callbacks.length; i += 1) {
            const callback = render_callbacks[i];
            if (!seen_callbacks.has(callback)) {
                // ...so guard against infinite loops
                seen_callbacks.add(callback);
                callback();
            }
        }
        render_callbacks.length = 0;
    } while (dirty_components.length);
    while (flush_callbacks.length) {
        flush_callbacks.pop()();
    }
    update_scheduled = false;
    flushing = false;
    seen_callbacks.clear();
}
function update($$) {
    if ($$.fragment !== null) {
        $$.update();
        run_all($$.before_update);
        const dirty = $$.dirty;
        $$.dirty = [-1];
        $$.fragment && $$.fragment.p($$.ctx, dirty);
        $$.after_update.forEach(add_render_callback);
    }
}
const outroing = new Set();
function transition_in(block, local) {
    if (block && block.i) {
        outroing.delete(block);
        block.i(local);
    }
}
function mount_component(component, target, anchor, customElement) {
    const { fragment, on_mount, on_destroy, after_update } = component.$$;
    fragment && fragment.m(target, anchor);
    if (!customElement) {
        // onMount happens before the initial afterUpdate
        add_render_callback(() => {
            const new_on_destroy = on_mount.map(run).filter(is_function);
            if (on_destroy) {
                on_destroy.push(...new_on_destroy);
            }
            else {
                // Edge case - component was destroyed immediately,
                // most likely as a result of a binding initialising
                run_all(new_on_destroy);
            }
            component.$$.on_mount = [];
        });
    }
    after_update.forEach(add_render_callback);
}
function destroy_component(component, detaching) {
    const $$ = component.$$;
    if ($$.fragment !== null) {
        run_all($$.on_destroy);
        $$.fragment && $$.fragment.d(detaching);
        // TODO null out other refs, including component.$$ (but need to
        // preserve final state?)
        $$.on_destroy = $$.fragment = null;
        $$.ctx = [];
    }
}
function make_dirty(component, i) {
    if (component.$$.dirty[0] === -1) {
        dirty_components.push(component);
        schedule_update();
        component.$$.dirty.fill(0);
    }
    component.$$.dirty[(i / 31) | 0] |= (1 << (i % 31));
}
function init(component, options, instance, create_fragment, not_equal, props, dirty = [-1]) {
    const parent_component = current_component;
    set_current_component(component);
    const $$ = component.$$ = {
        fragment: null,
        ctx: null,
        // state
        props,
        update: noop,
        not_equal,
        bound: blank_object(),
        // lifecycle
        on_mount: [],
        on_destroy: [],
        on_disconnect: [],
        before_update: [],
        after_update: [],
        context: new Map(parent_component ? parent_component.$$.context : options.context || []),
        // everything else
        callbacks: blank_object(),
        dirty,
        skip_bound: false
    };
    let ready = false;
    $$.ctx = instance
        ? instance(component, options.props || {}, (i, ret, ...rest) => {
            const value = rest.length ? rest[0] : ret;
            if ($$.ctx && not_equal($$.ctx[i], $$.ctx[i] = value)) {
                if (!$$.skip_bound && $$.bound[i])
                    $$.bound[i](value);
                if (ready)
                    make_dirty(component, i);
            }
            return ret;
        })
        : [];
    $$.update();
    ready = true;
    run_all($$.before_update);
    // `false` as a special case of no DOM component
    $$.fragment = create_fragment ? create_fragment($$.ctx) : false;
    if (options.target) {
        if (options.hydrate) {
            start_hydrating();
            const nodes = children(options.target);
            // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
            $$.fragment && $$.fragment.l(nodes);
            nodes.forEach(detach);
        }
        else {
            // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
            $$.fragment && $$.fragment.c();
        }
        if (options.intro)
            transition_in(component.$$.fragment);
        mount_component(component, options.target, options.anchor, options.customElement);
        end_hydrating();
        flush();
    }
    set_current_component(parent_component);
}
/**
 * Base class for Svelte components. Used when dev=false.
 */
class SvelteComponent {
    $destroy() {
        destroy_component(this, 1);
        this.$destroy = noop;
    }
    $on(type, callback) {
        const callbacks = (this.$$.callbacks[type] || (this.$$.callbacks[type] = []));
        callbacks.push(callback);
        return () => {
            const index = callbacks.indexOf(callback);
            if (index !== -1)
                callbacks.splice(index, 1);
        };
    }
    $set($$props) {
        if (this.$$set && !is_empty($$props)) {
            this.$$.skip_bound = true;
            this.$$set($$props);
            this.$$.skip_bound = false;
        }
    }
}

/* src/Lines.svelte generated by Svelte v3.38.3 */

function get_each_context(ctx, list, i) {
	const child_ctx = ctx.slice();
	child_ctx[5] = list[i];
	return child_ctx;
}

// (26:0) {#if show}
function create_if_block$1(ctx) {
	let svg;
	let g;
	let each_value = /*lines*/ ctx[3];
	let each_blocks = [];

	for (let i = 0; i < each_value.length; i += 1) {
		each_blocks[i] = create_each_block(get_each_context(ctx, each_value, i));
	}

	return {
		c() {
			svg = svg_element("svg");
			g = svg_element("g");

			for (let i = 0; i < each_blocks.length; i += 1) {
				each_blocks[i].c();
			}

			attr(g, "stroke-width", "4");
			attr(g, "stroke-linecap", "round");
			attr(svg, "height", /*size*/ ctx[0]);
			attr(svg, "stroke", /*colour*/ ctx[1]);
			attr(svg, "viewBox", "0 0 64 64");
		},
		m(target, anchor) {
			insert(target, svg, anchor);
			append(svg, g);

			for (let i = 0; i < each_blocks.length; i += 1) {
				each_blocks[i].m(g, null);
			}
		},
		p(ctx, dirty) {
			if (dirty & /*lines*/ 8) {
				each_value = /*lines*/ ctx[3];
				let i;

				for (i = 0; i < each_value.length; i += 1) {
					const child_ctx = get_each_context(ctx, each_value, i);

					if (each_blocks[i]) {
						each_blocks[i].p(child_ctx, dirty);
					} else {
						each_blocks[i] = create_each_block(child_ctx);
						each_blocks[i].c();
						each_blocks[i].m(g, null);
					}
				}

				for (; i < each_blocks.length; i += 1) {
					each_blocks[i].d(1);
				}

				each_blocks.length = each_value.length;
			}

			if (dirty & /*size*/ 1) {
				attr(svg, "height", /*size*/ ctx[0]);
			}

			if (dirty & /*colour*/ 2) {
				attr(svg, "stroke", /*colour*/ ctx[1]);
			}
		},
		d(detaching) {
			if (detaching) detach(svg);
			destroy_each(each_blocks, detaching);
		}
	};
}

// (29:6) {#each lines as line}
function create_each_block(ctx) {
	let line;
	let animate;

	return {
		c() {
			line = svg_element("line");
			animate = svg_element("animate");
			attr(animate, "attributeName", "stroke-opacity");
			attr(animate, "dur", "1000ms");
			attr(animate, "values", /*line*/ ctx[5].opacityKeyframes);
			attr(animate, "repeatCount", "indefinite");
			attr(line, "y1", "12");
			attr(line, "y2", "20");
			attr(line, "transform", "translate(32,32) rotate(" + /*line*/ ctx[5].angle + ")");
		},
		m(target, anchor) {
			insert(target, line, anchor);
			append(line, animate);
		},
		p: noop,
		d(detaching) {
			if (detaching) detach(line);
		}
	};
}

function create_fragment$1(ctx) {
	let if_block_anchor;
	let if_block = /*show*/ ctx[2] && create_if_block$1(ctx);

	return {
		c() {
			if (if_block) if_block.c();
			if_block_anchor = empty();
		},
		m(target, anchor) {
			if (if_block) if_block.m(target, anchor);
			insert(target, if_block_anchor, anchor);
		},
		p(ctx, [dirty]) {
			if (/*show*/ ctx[2]) {
				if (if_block) {
					if_block.p(ctx, dirty);
				} else {
					if_block = create_if_block$1(ctx);
					if_block.c();
					if_block.m(if_block_anchor.parentNode, if_block_anchor);
				}
			} else if (if_block) {
				if_block.d(1);
				if_block = null;
			}
		},
		i: noop,
		o: noop,
		d(detaching) {
			if (if_block) if_block.d(detaching);
			if (detaching) detach(if_block_anchor);
		}
	};
}

function instance$1($$self, $$props, $$invalidate) {
	let { size = 32 } = $$props;
	let { colour = "currentColor" } = $$props;
	let { show = true } = $$props;

	// Lines animation
	const values = {
		angles: [180, 210, 240, 270, 300, 330, 0, 30, 60, 90, 120, 150],
		opacityKeyframes: [1, 0.85, 0.7, 0.65, 0.55, 0.45, 0.35, 0.25, 0.15, 0.1, 0]
	};

	const lines = [];

	values.angles.forEach((angle, index) => {
		let opacityKeyframes = [...values.opacityKeyframes];
		opacityKeyframes = opacityKeyframes.splice(opacityKeyframes.length - index).concat(opacityKeyframes); // Rotate the opacity keyframe values, once per line.
		opacityKeyframes.push(opacityKeyframes[0]); // Repeat the initial opacity.
		opacityKeyframes = opacityKeyframes.join(";");
		lines.push({ angle, opacityKeyframes });
	});

	$$self.$$set = $$props => {
		if ("size" in $$props) $$invalidate(0, size = $$props.size);
		if ("colour" in $$props) $$invalidate(1, colour = $$props.colour);
		if ("show" in $$props) $$invalidate(2, show = $$props.show);
	};

	return [size, colour, show, lines];
}

class Lines extends SvelteComponent {
	constructor(options) {
		super();
		init(this, options, instance$1, create_fragment$1, safe_not_equal, { size: 0, colour: 1, show: 2 });
	}
}

/* src/Dots.svelte generated by Svelte v3.38.3 */

function create_if_block(ctx) {
	let svg;
	let g;
	let circle0;
	let animate0;
	let animate1;
	let circle1;
	let animate2;
	let animate3;
	let circle2;
	let animate4;
	let animate5;

	return {
		c() {
			svg = svg_element("svg");
			g = svg_element("g");
			circle0 = svg_element("circle");
			animate0 = svg_element("animate");
			animate1 = svg_element("animate");
			circle1 = svg_element("circle");
			animate2 = svg_element("animate");
			animate3 = svg_element("animate");
			circle2 = svg_element("circle");
			animate4 = svg_element("animate");
			animate5 = svg_element("animate");
			attr(animate0, "attributeName", "fill-opacity");
			attr(animate0, "dur", "750ms");
			attr(animate0, "values", ".5;.6;.8;1;.8;.6;.5;.5");
			attr(animate0, "repeatCount", "indefinite");
			attr(animate1, "attributeName", "r");
			attr(animate1, "dur", "750ms");
			attr(animate1, "values", "3;3;4;5;6;5;4;3");
			attr(animate1, "repeatCount", "indefinite");
			attr(circle0, "cx", "16");
			attr(circle0, "cy", "32");
			attr(circle0, "stroke-width", "0");
			attr(animate2, "attributeName", "fill-opacity");
			attr(animate2, "dur", "750ms");
			attr(animate2, "values", ".5;.5;.6;.8;1;.8;.6;.5");
			attr(animate2, "repeatCount", "indefinite");
			attr(animate3, "attributeName", "r");
			attr(animate3, "dur", "750ms");
			attr(animate3, "values", "4;3;3;4;5;6;5;4");
			attr(animate3, "repeatCount", "indefinite");
			attr(circle1, "cx", "32");
			attr(circle1, "cy", "32");
			attr(circle1, "stroke-width", "0");
			attr(animate4, "attributeName", "fill-opacity");
			attr(animate4, "dur", "750ms");
			attr(animate4, "values", ".6;.5;.5;.6;.8;1;.8;.6");
			attr(animate4, "repeatCount", "indefinite");
			attr(animate5, "attributeName", "r");
			attr(animate5, "dur", "750ms");
			attr(animate5, "values", "5;4;3;3;4;5;6;5");
			attr(animate5, "repeatCount", "indefinite");
			attr(circle2, "cx", "48");
			attr(circle2, "cy", "32");
			attr(circle2, "stroke-width", "0");
			attr(svg, "height", /*size*/ ctx[0]);
			attr(svg, "fill", /*colour*/ ctx[1]);
			attr(svg, "viewBox", "0 0 64 64");
		},
		m(target, anchor) {
			insert(target, svg, anchor);
			append(svg, g);
			append(g, circle0);
			append(circle0, animate0);
			append(circle0, animate1);
			append(g, circle1);
			append(circle1, animate2);
			append(circle1, animate3);
			append(g, circle2);
			append(circle2, animate4);
			append(circle2, animate5);
		},
		p(ctx, dirty) {
			if (dirty & /*size*/ 1) {
				attr(svg, "height", /*size*/ ctx[0]);
			}

			if (dirty & /*colour*/ 2) {
				attr(svg, "fill", /*colour*/ ctx[1]);
			}
		},
		d(detaching) {
			if (detaching) detach(svg);
		}
	};
}

function create_fragment(ctx) {
	let if_block_anchor;
	let if_block = /*show*/ ctx[2] && create_if_block(ctx);

	return {
		c() {
			if (if_block) if_block.c();
			if_block_anchor = empty();
		},
		m(target, anchor) {
			if (if_block) if_block.m(target, anchor);
			insert(target, if_block_anchor, anchor);
		},
		p(ctx, [dirty]) {
			if (/*show*/ ctx[2]) {
				if (if_block) {
					if_block.p(ctx, dirty);
				} else {
					if_block = create_if_block(ctx);
					if_block.c();
					if_block.m(if_block_anchor.parentNode, if_block_anchor);
				}
			} else if (if_block) {
				if_block.d(1);
				if_block = null;
			}
		},
		i: noop,
		o: noop,
		d(detaching) {
			if (if_block) if_block.d(detaching);
			if (detaching) detach(if_block_anchor);
		}
	};
}

function instance($$self, $$props, $$invalidate) {
	let { size = 32 } = $$props;
	let { colour = "currentColor" } = $$props;
	let { show = true } = $$props;

	$$self.$$set = $$props => {
		if ("size" in $$props) $$invalidate(0, size = $$props.size);
		if ("colour" in $$props) $$invalidate(1, colour = $$props.colour);
		if ("show" in $$props) $$invalidate(2, show = $$props.show);
	};

	return [size, colour, show];
}

class Dots extends SvelteComponent {
	constructor(options) {
		super();
		init(this, options, instance, create_fragment, safe_not_equal, { size: 0, colour: 1, show: 2 });
	}
}

export { Dots, Lines };
