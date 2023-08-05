package main

import (
	"fmt"
	"os"
)

// Single line comment

/*
Multi-line comment
*/

var pl = fmt.Println // fmt.Println alias

var age int

func add(x int, y int) (z int) {
	return x + y
}

func testing() {
	panic("Not implemented.")
}

var globalVariable string = "This is a global variable"

const globalConstant string = "This is a global constant"

func main() {
	testing()
	fmt.Println(globalVariable)
	fmt.Println(globalConstant)
	// Types
	// Numbers
	var integer int = 0            // Between 32 and 64 bits wide depending on the system.
	var integer8 int8 = 0          // Goes from -127 to 128.
	var unsignedInteger8 uint8 = 0 // Goes from 0 to 255.
	fmt.Println(integer, integer8, unsignedInteger8, "|", "1 + 1 =", 1+1)
	// Floats
	var ( // also works with const.
		floatingPoint32  float32    = 0.0 // Single precision.
		floatingPoint64  float64    = 0.0 // Double precision, prefered type for floats.
		complexNumber64  complex64  = 0 + 0i
		complexNumber128 complex128 = 0 + 0i
	)
	fmt.Println(floatingPoint32, floatingPoint64, complexNumber64, complexNumber128, "|", "1.01 - 0.99 =", 1.01-0.99)
	// Strings
	var helloWorld string = "Hello World!"
	fmt.Println(len(helloWorld), helloWorld[0], "Hello"+"World"+"Without"+"Spaces")
	// Booleans
	/*
		&& and
		|| or
		! not

		Can't use keywords like Python.
	*/
	var trueBoolean bool = true
	var falseBoolean bool = false
	fmt.Println(
		trueBoolean && trueBoolean,
		trueBoolean && falseBoolean,
		trueBoolean || trueBoolean,
		trueBoolean || falseBoolean,
		!trueBoolean,
	)

	// Variables
	var x int = 1
	y := 1    // Short declaration, only works in functions. Also infer the type based on the literal value. Should be used whenever possible.
	var z = 1 // Type can also be infered with normal declarations.
	fmt.Println(x, y, z)

	// Control Structures
	i := 1
	for i <= 10 { // Equivalent to a while-loop
		//fmt.Println(i)
		i += 1 // i++ would also work.
	}

	for j := 1; j <= 10; j++ { // Equivalent to a traditional for-loop
		if j%2 == 0 {
			fmt.Println(j, "Even")
		} else { // Else-if example: else if i % 3 == 0 {}
			fmt.Println(j, "Odd")
		}
	}

	i = 0 // Reset i variable
	for i <= 5 {
		switch i {
		case 0:
			fmt.Println("Zero")
		case 1:
			fmt.Println("One")
		case 2:
			fmt.Println("Two")
		case 3:
			fmt.Println("Three")
		case 4:
			fmt.Println("Four")
		case 5:
			fmt.Println("Five")
		default:
			fmt.Println("NaN")
		}
		i++
	}

	// Arrays, Slices, and Maps
	// Arrays
	var intArrayOne [5]int
	intArrayOne[4] = 100
	var intArrayTwo = [5]int{0, 0, 0, 0, 100}
	fmt.Println(intArrayTwo)
	intArray := [5]int{0, 0, 0, 0, 100}
	fmt.Println(intArray)
	fmt.Println(intArray[4])

	var total int = 0
	for _, value := range intArray { // for index, value := range array {}
		total += value
	}
	fmt.Println("Average:", total/len(intArray))

	// Slices
	intSlice := intArray[:2]
	fmt.Println("intSlice:", intSlice)
	intSlice = append(intSlice, 2, 3)
	fmt.Println("intSlice:", intSlice)
	intSlice = make([]int, len(intArray))
	copy(intSlice, intArray[:])
	fmt.Println("intSlice:", intSlice)
	// TODO Does modifying a slice modify the underlying array?

	// Maps
	//var aMap map[string]int  // Will return a compile-time error.
	aMap := make(map[string]int)
	aMap["key"] = 42
	fmt.Println(aMap)
	fmt.Println(aMap["key"])
	delete(aMap, "key")
	fmt.Println(aMap)
	fmt.Println(aMap["key"]) // Will not return a key-error but 0 instead.
	value, found := aMap["key"]
	fmt.Println(value, found) // 0 false
	if value, found := aMap["key"]; found {
		fmt.Println(value)
	}
	elements := map[string]string{
		"H": "Hydrogen",
		"C": "Carbon",
		"O": "Oxygen",
	}
	fmt.Println(elements)
	complexElements := map[string]map[string]string{
		"H": map[string]string{
			"name":  "Hydrogen",
			"state": "gaz",
		},
		"C": map[string]string{
			"name":  "Carbon",
			"state": "solid",
		},
		"O": map[string]string{
			"name":  "Oxygen",
			"state": "gaz",
		},
	}
	fmt.Println(complexElements)

	// Functions
	pl("%T", pl)
	fmt.Println("%d", age)
	fmt.Println("Hello World!")
	fmt.Println("Enter age")
	fmt.Println(add(1, 1))
	/*
		reader := bufio.NewReader(os.Stdin)
		age, err := reader.ReadString('\n')
		if err != nil {
			log.Fatal(err)
		}
		fmt.Println(age)
	*/
	os.Exit(0)
}
