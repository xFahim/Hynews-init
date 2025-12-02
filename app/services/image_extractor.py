"""Image extraction utilities for article scraping."""

from bs4 import BeautifulSoup
from lxml import etree
from typing import Optional, Tuple
from urllib.parse import urljoin


class ImageExtractor:
    """Extracts article images from HTML content."""

    BASE_URL = "https://www.thedailystar.net"

    @staticmethod
    def extract_image_url(soup: BeautifulSoup) -> str:
        """
        Extract article image URL from BeautifulSoup parsed HTML.

        Args:
            soup: BeautifulSoup object of the article page.

        Returns:
            Image URL string, empty if no valid article image found.
        """
        # Primary method: Use the main image wrapped in span with .section-media .lg-gallery
        # This is usually the cleanest URL for the lightbox gallery
        image_element = soup.select_one(".section-media .lg-gallery")

        if image_element:
            image_url = image_element.get("data-src")
            if image_url:
                # Convert to absolute URL if needed
                if isinstance(image_url, list):
                    image_url = image_url[0] if image_url else ""
                image_url = str(image_url).strip()

                if image_url:
                    # Convert to absolute URL
                    if image_url.startswith("http"):
                        return image_url
                    elif image_url.startswith("//"):
                        return "https:" + image_url
                    elif image_url.startswith("/"):
                        return urljoin(ImageExtractor.BASE_URL, image_url)
                    else:
                        return urljoin(ImageExtractor.BASE_URL, "/" + image_url)

        # Fallback: Use BeautifulSoup approach directly (more reliable)
        image_elem = ImageExtractor._find_image_with_bs4(soup)

        # Fallback to XPath if BeautifulSoup didn't work
        if not image_elem:
            html_str = str(soup)
            tree = etree.HTML(html_str)
            xpath_selector = '//*[contains(concat( " ", @class, " " ), concat( " ", "lg-gallery", " " ))]//picture[.//img[contains(concat( " ", @class, " " ), concat( " ", "lazyloaded", " " ))]]'
            picture_results = tree.xpath(xpath_selector)

            if picture_results:
                picture_elem = picture_results[0]
                source_elem = picture_elem.xpath(".//source[@srcset or @data-srcset]")
                if source_elem:
                    image_elem = source_elem[0]
                else:
                    img_elem = picture_elem.xpath(".//img[@srcset or @data-srcset]")
                    if img_elem:
                        image_elem = img_elem[0]

        if not image_elem:
            return ""

        # Extract URL from the element
        url = ImageExtractor._extract_url_from_element(image_elem)

        # Double-check: if we got a URL but it's from the wrong domain, return empty
        if url and "tds-images-bn.thedailystar.net" in url.lower():
            return ""

        return url

    @staticmethod
    def _find_image_with_bs4(soup: BeautifulSoup) -> Optional[etree.Element]:
        """
        Find article image using BeautifulSoup.

        Args:
            soup: BeautifulSoup object of the article page.

        Returns:
            lxml element with image, or None if not found.
        """
        all_picture_tags = soup.find_all("picture")

        # If no picture tags found, return None
        if not all_picture_tags:
            return None

        candidate_pictures = []

        for picture_tag in all_picture_tags:
            is_article_image, skip_image = ImageExtractor._is_valid_article_image(
                picture_tag
            )

            # Only skip if we're sure it's not an article image AND it should be skipped
            # If we found a valid article image, don't skip even if there are some skip-worthy elements
            if skip_image and not is_article_image:
                continue

            # Only add if it's a valid article image
            if is_article_image:
                priority = ImageExtractor._get_image_priority(picture_tag)
                candidate_pictures.append((priority, picture_tag))

        # Sort by priority (higher quality images first)
        candidate_pictures.sort(key=lambda x: x[0])

        # Process candidates
        for priority, picture_tag in candidate_pictures:
            source_tag = ImageExtractor._find_source_tag(picture_tag)
            if source_tag:
                source_html = str(source_tag)
                source_tree = etree.HTML(source_html)
                if source_tree is not None:
                    source_elem = source_tree.xpath("//source[@srcset or @data-srcset]")
                    if source_elem:
                        return source_elem[0]

            img_tag = ImageExtractor._find_img_tag(picture_tag)
            if img_tag:
                img_html = str(img_tag)
                img_tree = etree.HTML(img_html)
                if img_tree is not None:
                    img_elem = img_tree.xpath("//img[@srcset or @data-srcset]")
                    if img_elem:
                        return img_elem[0]

        return None

    @staticmethod
    def _is_valid_article_image(picture_tag) -> Tuple[bool, bool]:
        """
        Check if picture tag contains a valid article image.

        Args:
            picture_tag: BeautifulSoup picture tag element.

        Returns:
            Tuple of (is_article_image, skip_image).
        """
        is_article_image = False
        has_bn_domain = False
        has_author_image = False

        sources = picture_tag.find_all("source")
        imgs = picture_tag.find_all("img")
        all_elements = list(sources) + list(imgs)

        # Check all elements to see what we have
        for element in all_elements:
            srcset_attr = element.get("srcset") or element.get("data-srcset")
            if not srcset_attr:
                continue

            srcset = (
                " ".join(srcset_attr)
                if isinstance(srcset_attr, list)
                else str(srcset_attr)
            )
            srcset_lower = srcset.lower()

            # Check for valid article images
            if "tds-images.thedailystar.net" in srcset_lower:
                # Make sure it's not an author image
                if "author" not in srcset_lower and "/small_" not in srcset_lower:
                    is_article_image = True
                else:
                    has_author_image = True
            # Check for -bn domain (site images/logos - always skip)
            elif "tds-images-bn.thedailystar.net" in srcset_lower:
                has_bn_domain = True

        # Skip if we found -bn domain images (site logos)
        # Or if we only found author/small images and no valid article images
        skip_image = has_bn_domain or (has_author_image and not is_article_image)

        return is_article_image, skip_image

    @staticmethod
    def _get_image_priority(picture_tag) -> int:
        """
        Get priority for image (lower number = higher priority).

        Args:
            picture_tag: BeautifulSoup picture tag element.

        Returns:
            Priority integer (0 = highest, 1 = lower).
        """
        priority = 1
        sources = picture_tag.find_all("source")

        for source in sources:
            srcset_attr = source.get("srcset") or source.get("data-srcset")
            if srcset_attr:
                srcset = (
                    " ".join(srcset_attr)
                    if isinstance(srcset_attr, list)
                    else str(srcset_attr)
                )
                if "/big_" in srcset.lower():
                    priority = 0
                    break

        return priority

    @staticmethod
    def _find_source_tag(picture_tag):
        """Find source tag with srcset/data-srcset in picture tag."""
        sources = picture_tag.find_all("source")
        for source in sources:
            if source.get("srcset") or source.get("data-srcset"):
                return source
        return None

    @staticmethod
    def _find_img_tag(picture_tag):
        """Find img tag with srcset/data-srcset in picture tag."""
        img_tags = picture_tag.find_all("img")
        for img_tag in img_tags:
            if img_tag.get("srcset") or img_tag.get("data-srcset"):
                return img_tag
        return None

    @staticmethod
    def _extract_url_from_element(image_elem) -> str:
        """
        Extract URL from lxml element.

        Args:
            image_elem: lxml element with image attributes.

        Returns:
            Extracted image URL.
        """
        src_attr = None
        for attr in ["srcset", "data-srcset", "src", "data-src"]:
            attr_value = image_elem.get(attr)
            if attr_value:
                src_attr = attr_value
                break

        if not src_attr:
            return ""

        # Ensure src_attr is a string
        if isinstance(src_attr, list):
            src_attr = src_attr[0] if src_attr else ""
        src_attr = str(src_attr).strip()

        if not src_attr:
            return ""

        # Extract first URL from srcset format
        if "," in src_attr:
            first_url = src_attr.split(",")[0].strip().split()[0].strip()
        elif " " in src_attr:
            first_url = src_attr.split()[0].strip()
        else:
            first_url = src_attr.strip()

        # Convert to absolute URL
        if first_url.startswith("http"):
            return first_url
        elif first_url.startswith("//"):
            return "https:" + first_url
        elif first_url.startswith("/"):
            return urljoin(ImageExtractor.BASE_URL, first_url)
        else:
            return urljoin(ImageExtractor.BASE_URL, "/" + first_url)
