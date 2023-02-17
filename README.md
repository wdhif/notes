# grimoire

> A grimoire (also known as a “book of spells”) is a textbook of magic, typically including instructions on how to create magical objects like talismans and amulets, how to perform magical spells, charms and divination, and how to summon or invoke supernatural entities such as angels, spirits, deities and demons.

My personal and dogmatic grimoire of algorithms, data structures and other knowledges. Use at your own risks.

```
      __...--~~~~~-._   _.-~~~~~--...__
    //               `V'               \\
   //                 |                 \\
  //__...--~~~~~~-._  |  _.-~~~~~~--...__\\
 //__.....----~~~~._\ | /_.~~~~----.....__\\
====================\\|//====================
                    `---`
```

## Website installation

The grimoire website is powered by [Hugo](https://gohugo.io). To build the website, you must first start by cloning the [Hugo Book](https://github.com/alex-shpak/hugo-book) theme which is managed by a submodule.

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
