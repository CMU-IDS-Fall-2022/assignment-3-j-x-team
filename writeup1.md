**Project Goals:**

We explored how to visualize the nationwide distribution of social capital metrics.  Our intended users are policymakers and social scientists;
by viewing our visualization, users can determine which areas of the country need the most support in developing social capital and which 
areas of the country already have high social capital values.  These policymakers and social scientists can leverage our visualization as a starting
point with which to identify regions to learn from and regions in which to implement programs intended to boost social capital.  
Further, the distributions of  social capital for each metric can be compared and contrasted to enable social scientists to generate new 
research questions.

**Design Rationale:**

We initially explored how to enable users to visualize the nationwide distribution of a selected social capital metric. We decided on a map of the US 
filled with points that leverage color to convey high-to-low levels of the selected metric. We determined that a user story of a policymaker using
this visualization might be, "As a policymaker, I need to see which regions of the U.S. have the highest and lowest levels of a selected
social capital metric so I can make an informed decision about where to prioritize program implementation." Considering this user story, we settled on
the map of the U.S. with colored dots as it is intuitive and responsive to the user's need. We also considered splitting the map of the U.S. into 
distinct regions and allowing the user to first click on a region to explore. However, we decided against this because the distribution of 
social capital might have a pattern that is not aligned with a North, South, East, West split. For example, there could be a high concentration of 
a given metric only in urban areas; it would be more intuitive to visualize this patter on a map of the whole U.S. rather than in a given region.

We decided to allow the user to examine details of a selected zipcode due to the likely user need to explore metrics that could be associated
with the given social capital metric. If a policymaker is considering implementing a program to enhance social capital in a selected city, for example,
they can see a list of key data about the city to inform implementation.

**Development Process**

First, our team met to collaboratively create our project goals and sketch our desired visualizations and features. Xinzhu implemented the U.S. map
visualizations and radio buttons that allow the user to toggle between nationwide visualizations. Meanwhile, Jimmy implemented the visualization and data 
rendered after the user clicks on a selected zipcode.

After meeting to collaboratively review our product, we added new data to our master dataframe pulled from another source, edited our tooltips,
and double-checked whether alternative visualizations would be more intuitive.

Roughly, each of us spent 15 hours in total on the project.  Data cleaning and troubleshooting Altair charts were the most time-consuming tasks.

**Success Story**

One insight generated from our project is the Deep South's relative lack of social capital. Policymakers seeking to identify areas for 
investment to increase social capital could use our map to identify the South as a target.
