Homebrew images (and related assets) for 5etools. See the [main homebrew repository](https://github.com/TheGiddyLimit/homebrew).

##### Conventions to Follow

- A single `img/` subdirectory should be made per homebrew "JSON" source (e.g. `MyJsonSourceName` -> `img/MyJsonSourceName`). The structure/layout of this subdirectory can be tailored to suit.
- `.webp` images are preferred. 5etools uses:
  - Compressed, 85% quality `webp` for most images
  - Uncompressed `webp` for tokens
- Image links from data in the [main homebrew repository](https://github.com/TheGiddyLimit/homebrew) should be of the form:
  `https://raw.githubusercontent.com/TheGiddyLimit/homebrew-img/main/img/MyJsonSourceName/*.*`
  For example, as a standard `"image"`-type `entry`:
  ```
    {
        "type": "image",
        "href": {
            "type": "external",
            "url": "https://raw.githubusercontent.com/TheGiddyLimit/homebrew-img/main/img/MyJsonSourceName/creatures/example-image.webp"
        }
    }
  ```
