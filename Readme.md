# Market Melee
### Authors: Venn Reddy and Daniel Laij

## Inspiration
Our inspiration for Market Melee stemmed from the entire group taking an Introduction to Computational Investing class. After seeing how a lot of financial jargon, calculations, and visualizations are intimidating to the everyday person, we decided to build Market Melee to make stock market investing more accessible and engaging for everyone. By gamifying the investing experience, we aimed to create a platform where any user can learn, compete, and grow their financial knowledge in a fun environment.

## What it does
Market Melee is a web application that allows users to create and manage simulated stock portfolios using real-time market data. Having hundreds of stocks to choose from, notably from the S&P 500, they are able to allocate their investments and track their portfolio performance over time. Features include interactive graphs, detailed stock metrics, and a place to track your own progress against friends within your league.

## How we built it
We built Market Melee using Python and the Flask web framework for our backend, and utilized MongoDB Atlas as our database to store user information, and stock statistics. For our data analysis and visualization, we used libraries such as pandas, NumPy, and MatPlotLib to read stock information and generate performance graphs. The frontend was developed with HTML, CSS, with Bootstrap for responsive design, Javascript to add interactive features, and Jinja to wrap it all nicely with our Flask backend.

## Challenges we ran into
One of the main challenges we ran into was displaying our data visualization graphs onto our frontend, as we had to decide whether we were to store our images via cloud, storage, or make them temporary images. Furthermore, git version control was another massive hurdle we had to face, as oftentimes the backend and the frontend had conflicting files, which lead to multiple merge conflicts. Authentication and managing users was also a tough task, as we had to make sure users are only able to see their information, while also storing and utilizing other users' data at the same time.

## Accomplishments that we're proud of
We are proud of creating a platform that helps bridge the gap between stock investors and the everyday person. Furthermore, we are very happy about how our main features of individualized stock statistics and visualizations worked seamlessly with our frontend, which allows users to view individual stocks and learn more about them, using pop-up modals to learn more about stock statistics, such as daily returns, volatility, and even the Sharpe Ratio. 

## What we learned
While developing Market Melee, we improved our ability to work with a foreign stack for web development, as navigating through this was slow at first. Furthermore, we learned how to effectively leverage document-oriented databases like MongoDB and Flask for routing and session management. Furthermore, we strengthened our ability to delegate tasks in order to have a smooth work flow and proper code management.

## What's next for Market Melee
Looking in the future, we plan on incorporate real-time stock data APIs to provide users with the most current market information. We also hope to implement machine learning and more advanced algorithms to help users leverage technology to their advantage to profit from the stock market. In addition, we would want to implement more educational resources within the platforms to help users grow financial literacy and their own portfolios. 