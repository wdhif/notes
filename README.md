# notes

My personal and dogmatic notes about algorithms, data structures and other knowledges. Use at your own risks.

## Website installation

My notes are powered by [Hugo](https://gohugo.io). To build the website, you must first start by cloning the [Hugo Book](https://github.com/alex-shpak/hugo-book) theme which is managed by a submodule.

```
git submodule init
git submodule update
```

Run hugo server
```
docker run --rm -it -v $(pwd)/website:/src -v $(pwd)/docs:/docs -p 1313:1313 klakegg/hugo:ext-alpine server
```

Build website
```
docker run --rm -it -v $(pwd)/website:/src -v $(pwd)/docs:/docs klakegg/hugo:ext-alpine
```
