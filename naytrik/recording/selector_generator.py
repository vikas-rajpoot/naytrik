"""
Multi-strategy selector generator for robust element finding.

This module generates multiple fallback strategies to find elements on a page,
reducing dependence on AI and making workflows more deterministic.
"""

import logging
from typing import Any, Dict, List, Optional

from naytrik.schema.selectors import (
    SelectorStrategy,
    SelectorType,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SelectorGenerator:
    """
    Generate multiple robust selector strategies from element data.

    This class takes element data captured during workflow recording and generates
    a prioritized list of strategies to find that element during execution.

    The strategies are ordered by reliability:
    1. ID selectors (most stable)
    2. Data attributes (very stable)
    3. Name attributes (stable for forms)
    4. Exact text match (good for links/buttons)
    5. ARIA labels (accessibility-based)
    6. Role + text (semantic HTML)
    7. Placeholder (for inputs)
    8. Title attribute (tooltips)
    9. Alt text (for images)
    10. Fuzzy text match (resilient to small changes)
    11. CSS selector (structural fallback)
    12. XPath (most powerful fallback)
    13. Coordinates (last resort)
    """

    def generate_strategies(
        self, 
        element_data: Dict[str, Any], 
        include_xpath_fallback: bool = True,
        include_css_fallback: bool = True,
    ) -> List[SelectorStrategy]:
        """
        Generate selector strategies from captured element data.

        Generates semantic strategies first, then optionally adds XPath/CSS fallbacks.

        Args:
            element_data: Dictionary containing:
                - tag_name: str (e.g., 'a', 'button', 'input')
                - text: str (visible text content)
                - attributes: Dict[str, str] (element attributes)
                - xpath: str (optional, pre-computed XPath)
                - css_selector: str (optional, pre-computed CSS selector)
            include_xpath_fallback: If True, include XPath as a fallback
            include_css_fallback: If True, include CSS selector as a fallback

        Returns:
            List of SelectorStrategy objects, ordered by priority

        Example:
            >>> generator = SelectorGenerator()
            >>> strategies = generator.generate_strategies(
            ...     {
            ...         'tag_name': 'button',
            ...         'text': 'Submit',
            ...         'attributes': {'id': 'submit-btn', 'aria-label': 'Submit form'},
            ...     }
            ... )
            >>> # Returns: id, text_exact, aria_label, role_text, text_fuzzy, xpath
        """
        strategies = []
        priority = 1
        
        tag = element_data.get('tag_name', '').lower()
        text = element_data.get('text', '').strip()
        attrs = element_data.get('attributes', {})

        # Strategy 1: ID selector (highest priority - most stable)
        if 'id' in attrs and attrs['id']:
            strategies.append(
                SelectorStrategy(
                    type=SelectorType.ID,
                    value=attrs['id'],
                    priority=priority,
                    metadata={'tag': tag},
                )
            )
            priority += 1

        # Strategy 2: Data attributes (very stable)
        data_attrs = {k: v for k, v in attrs.items() if k.startswith('data-') and v}
        if data_attrs:
            # Use the first data attribute
            key, value = next(iter(data_attrs.items()))
            strategies.append(
                SelectorStrategy(
                    type=SelectorType.DATA_ATTR,
                    value=value,
                    priority=priority,
                    metadata={'tag': tag, 'attribute': key},
                )
            )
            priority += 1

        # Strategy 3: Name attribute (stable for forms)
        if 'name' in attrs and attrs['name']:
            strategies.append(
                SelectorStrategy(
                    type=SelectorType.NAME,
                    value=attrs['name'],
                    priority=priority,
                    metadata={'tag': tag},
                )
            )
            priority += 1

        # Strategy 4: Test ID (if present - common in test frameworks)
        test_id_attrs = ['data-testid', 'data-test-id', 'data-test']
        for test_attr in test_id_attrs:
            if test_attr in attrs and attrs[test_attr]:
                strategies.append(
                    SelectorStrategy(
                        type=SelectorType.TEST_ID,
                        value=attrs[test_attr],
                        priority=priority,
                        metadata={'tag': tag, 'attribute': test_attr},
                    )
                )
                priority += 1
                break

        # Strategy 5: Exact text match (good for buttons/links)
        if text:
            strategies.append(
                SelectorStrategy(
                    type=SelectorType.TEXT_EXACT,
                    value=text,
                    priority=priority,
                    metadata={'tag': tag},
                )
            )
            priority += 1

        # Strategy 6: ARIA label (accessibility-based)
        if 'aria-label' in attrs and attrs['aria-label']:
            strategies.append(
                SelectorStrategy(
                    type=SelectorType.ARIA_LABEL,
                    value=attrs['aria-label'],
                    priority=priority,
                    metadata={'tag': tag},
                )
            )
            priority += 1

        # Strategy 7: Role + text (semantic HTML)
        role = self._infer_role(tag, attrs)
        if role and text:
            strategies.append(
                SelectorStrategy(
                    type=SelectorType.ROLE_TEXT,
                    value=text,
                    priority=priority,
                    metadata={'role': role, 'tag': tag},
                )
            )
            priority += 1

        # Strategy 8: Placeholder (for input fields)
        if 'placeholder' in attrs and attrs['placeholder']:
            strategies.append(
                SelectorStrategy(
                    type=SelectorType.PLACEHOLDER,
                    value=attrs['placeholder'],
                    priority=priority,
                    metadata={'tag': tag},
                )
            )
            priority += 1

        # Strategy 9: Title attribute (tooltip text)
        if 'title' in attrs and attrs['title']:
            strategies.append(
                SelectorStrategy(
                    type=SelectorType.TITLE,
                    value=attrs['title'],
                    priority=priority,
                    metadata={'tag': tag},
                )
            )
            priority += 1

        # Strategy 10: Alt text (for images)
        if 'alt' in attrs and attrs['alt']:
            strategies.append(
                SelectorStrategy(
                    type=SelectorType.ALT_TEXT,
                    value=attrs['alt'],
                    priority=priority,
                    metadata={'tag': tag},
                )
            )
            priority += 1

        # Strategy 11: Fuzzy text match (fallback - handles typos/variations)
        if text and len(text) > 3:  # Only for meaningful text
            strategies.append(
                SelectorStrategy(
                    type=SelectorType.TEXT_FUZZY,
                    value=text,
                    priority=priority,
                    metadata={'threshold': 0.8, 'tag': tag},
                )
            )
            priority += 1

        # Strategy 12: CSS selector fallback (if provided or generated)
        if include_css_fallback:
            css_selector = element_data.get('css_selector') or self._generate_css_selector(tag, text, attrs)
            if css_selector:
                strategies.append(
                    SelectorStrategy(
                        type=SelectorType.CSS,
                        value=css_selector,
                        priority=priority,
                        metadata={'tag': tag, 'fallback': True},
                    )
                )
                priority += 1

        # Strategy 13: XPath fallback (lowest priority but most powerful)
        if include_xpath_fallback:
            xpath = element_data.get('xpath') or self._generate_xpath(tag, text, attrs)
            if xpath:
                strategies.append(
                    SelectorStrategy(
                        type=SelectorType.XPATH,
                        value=xpath,
                        priority=priority,
                        metadata={'tag': tag, 'fallback': True},
                    )
                )
                priority += 1

        # Sort by priority (lower number = higher priority)
        strategies.sort(key=lambda s: s.priority)

        return strategies

    def _infer_role(self, tag: str, attrs: Dict[str, Any]) -> Optional[str]:
        """
        Infer semantic role from HTML tag and attributes.

        Args:
            tag: HTML tag name (e.g., 'button', 'a', 'input')
            attrs: Element attributes

        Returns:
            Semantic role string or None
        """
        # Explicit role attribute takes precedence
        if 'role' in attrs:
            return attrs['role']

        # Infer from HTML tag
        role_map = {
            'button': 'button',
            'a': 'link',
            'input': 'textbox',
            'textarea': 'textbox',
            'select': 'combobox',
            'h1': 'heading',
            'h2': 'heading',
            'h3': 'heading',
            'h4': 'heading',
            'h5': 'heading',
            'h6': 'heading',
            'img': 'img',
            'table': 'table',
            'ul': 'list',
            'ol': 'list',
            'nav': 'navigation',
        }

        # Special case for input types
        if tag == 'input' and 'type' in attrs:
            input_type = attrs['type'].lower()
            if input_type == 'checkbox':
                return 'checkbox'
            elif input_type == 'radio':
                return 'radio'
            elif input_type == 'submit':
                return 'button'

        return role_map.get(tag)

    def _generate_xpath(self, tag: str, text: str, attrs: Dict[str, Any]) -> Optional[str]:
        """
        Generate a robust XPath selector from element data.

        Args:
            tag: HTML tag name
            text: Element text content
            attrs: Element attributes

        Returns:
            XPath string or None
        """
        try:
            xpath_parts = []

            # Start with tag
            if tag:
                xpath_parts.append(f'//{tag}')
            else:
                xpath_parts.append('//*')

            # Add attribute-based conditions (most reliable)
            conditions = []

            # ID is most stable
            if 'id' in attrs and attrs['id']:
                conditions.append(f'@id={self._escape_xpath_value(attrs["id"])}')

            # Name attribute (common for forms)
            elif 'name' in attrs and attrs['name']:
                conditions.append(f'@name={self._escape_xpath_value(attrs["name"])}')

            # Data attributes (very stable)
            elif any(k.startswith('data-') for k in attrs.keys()):
                for k, v in attrs.items():
                    if k.startswith('data-') and v:
                        conditions.append(f'@{k}={self._escape_xpath_value(v)}')
                        break

            # ARIA label
            elif 'aria-label' in attrs and attrs['aria-label']:
                conditions.append(f'@aria-label={self._escape_xpath_value(attrs["aria-label"])}')

            # Placeholder
            elif 'placeholder' in attrs and attrs['placeholder']:
                conditions.append(f'@placeholder={self._escape_xpath_value(attrs["placeholder"])}')

            # Text content (fallback)
            elif text:
                # Use contains for more robustness
                conditions.append(f'contains(text(), {self._escape_xpath_value(text)})')

            # Combine conditions
            if conditions:
                xpath_parts.append('[' + ' and '.join(conditions) + ']')

            return ''.join(xpath_parts) if len(xpath_parts) > 1 else None

        except Exception as e:
            logger.debug(f'Failed to generate XPath: {e}')
            return None

    def _generate_css_selector(self, tag: str, text: str, attrs: Dict[str, Any]) -> Optional[str]:
        """
        Generate a robust CSS selector from element data.

        Args:
            tag: HTML tag name
            text: Element text content
            attrs: Element attributes

        Returns:
            CSS selector string or None
        """
        try:
            parts = []

            # Start with tag
            if tag:
                parts.append(tag)

            # Add ID (most specific)
            if 'id' in attrs and attrs['id']:
                # CSS escaping for IDs with special characters
                id_val = attrs['id'].replace(':', '\\:').replace('.', '\\.')
                parts.append(f'#{id_val}')
                return ''.join(parts)

            # Add name attribute
            if 'name' in attrs and attrs['name']:
                parts.append(f'[name="{self._escape_quotes(attrs["name"])}"]')
                return ''.join(parts)

            # Add data attributes (very stable)
            for k, v in attrs.items():
                if k.startswith('data-') and v:
                    parts.append(f'[{k}="{self._escape_quotes(v)}"]')
                    return ''.join(parts)

            # Add aria-label
            if 'aria-label' in attrs and attrs['aria-label']:
                parts.append(f'[aria-label="{self._escape_quotes(attrs["aria-label"])}"]')
                return ''.join(parts)

            # Add placeholder
            if 'placeholder' in attrs and attrs['placeholder']:
                parts.append(f'[placeholder="{self._escape_quotes(attrs["placeholder"])}"]')
                return ''.join(parts)

            # If we only have tag and no good attributes, return None
            # (CSS can't select by text content reliably)
            return ''.join(parts) if len(parts) > 1 else None

        except Exception as e:
            logger.debug(f'Failed to generate CSS selector: {e}')
            return None

    def _escape_xpath_value(self, value: str) -> str:
        """
        Escape quotes in XPath values.

        Args:
            value: String to escape

        Returns:
            Escaped string suitable for XPath
        """
        # If value contains single quotes, use double quotes
        if "'" in value:
            if '"' in value:
                # Both types of quotes - use concat
                parts = value.split("'")
                return "concat('" + "', \"'\", '".join(parts) + "')"
            else:
                return f'"{value}"'
        else:
            return f"'{value}'"

    def _escape_quotes(self, value: str) -> str:
        """Escape quotes in CSS selector values."""
        return value.replace("'", "\\'").replace('"', '\\"')

    def get_summary(self, strategies: List[SelectorStrategy]) -> str:
        """
        Get a human-readable summary of strategies.

        Args:
            strategies: List of selector strategies

        Returns:
            Summary string
        """
        lines = [f'Generated {len(strategies)} selector strategies:']
        for i, s in enumerate(strategies[:5], 1):  # Show first 5
            value_preview = s.value[:50] + '...' if len(s.value) > 50 else s.value
            lines.append(f'  {i}. [priority {s.priority}] {s.type}: {value_preview}')
        if len(strategies) > 5:
            lines.append(f'  ... and {len(strategies) - 5} more')
        return '\n'.join(lines)
