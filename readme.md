= Picotron External Build
This is a pair of scripts for turning your picotron cart into a folder
of lua files you can edit externally and a skeleton p64 cart, that you
can open in picotron to edit other assets.

>	❗️
>
>	It is HIGHLY RECOMMENDED that you only run these scripts on backup
>	copies of your files. They have not been tested in real use, and
>	could very well irreplaceably damage files at this stage.
>	

== Usage

=== picotron_export.py

You must first use the export tool on a picotron cart to generate a skel.p64 file. This at least adds the @@code tag so the build script knows where to add your lua files back. It will also take any code already in the cart and break it up into a set of lua files.

```
$> python picotron_export.py

usage: picotron_export.py [-h] input_cart output_directory
```

The arguments are
- input_cart
	The path to the cart you want to export
- output_directory
	The directory which will receive the new lua and skel.p64 files.
	Recommended either empty or new

Example:
```
python picotron_export.py ./game.p64 ./external_build/
```


=== picotron_build.py

After creating an export dir containing lua files and the skel.p64 file, run the build script to put them back together.
The script will also paste in any new files created after the export (though you will still need to `include` them in your main.lua).
For new files, it will add a pod line, and it will update the pod modified time for any that have been modified since the pod line date. For these, it will also increment the revision.
Note that the revision will only increment when the build script will run, while picotron would be updating on every save.

```
$> python picotron_build.py

usage: picotron_build.py [-h] input_directory input_cart output_file
```

The arguments are
- input_directory
	The path to the directory full of lua files. This
	will likely be the folder you received from running the export.
- input_cart
	The skel.p64 cart from the export. It must contain a `:: main.lua` 'file'
	containing the `@@code` tag.
	Will default to the `skel.p64` file inside the `input_directory` if
	omitted
- output_cart
	The path to output the final to. 
	Will default to `out.p64` inside the `input_directory` if omitted.

Example
```
python picotron_build.py ./external_build/ ./external_build/game_skel.p64 ./game_final.p64
```